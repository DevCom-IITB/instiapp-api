from celery import shared_task
from django.utils.timezone import now


@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,
    queue='resobin_sync',
    rate_limit='200/m',
)
def sync_resobin_for_user(self, user_id):
    from users.models import UserProfile
    from calendarhub.models import ExternalCalendarAccount, ExternalCalendarEventCache
    from calendarhub.services.resobin_client import ResoBinInternalClient, ResoBinAPIError
    from calendarhub.services.aggregator import normalize_resobin_event
    from calendarhub.tasks.notifications import schedule_reminder, cancel_reminder_by_external_id
    from redis import Redis
    from django.conf import settings

    redis_client = Redis.from_url(getattr(settings, 'REDIS_URL', 'redis://localhost:6379/1'))
    lock_key = f'calendar:user:{user_id}:sync:resobin:lock'

    if not redis_client.set(lock_key, '1', nx=True, ex=60):
        return  # another worker is already syncing this user

    account = None
    try:
        user = UserProfile.objects.get(id=user_id)

        account, _ = ExternalCalendarAccount.objects.get_or_create(
            user=user,
            provider='resobin',
            defaults={
                'external_user_id': user.ldap_id or '',
                'status': ExternalCalendarAccount.Status.SYNCING,
            },
        )
        account.status = ExternalCalendarAccount.Status.SYNCING
        account.save(update_fields=['status'])

        client = ResoBinInternalClient()
        data = client.get_timetable(username=user.ldap_id or user.roll_no or '')

        old_ids = set(
            ExternalCalendarEventCache.objects
            .filter(user=user, provider='resobin')
            .values_list('external_event_id', flat=True)
        )
        new_ids = set()
        changed_months = set()

        all_items = (
            data.get('slots', [])
            + data.get('exams', [])
            + data.get('deadlines', [])
        )

        for item in all_items:
            event_id = item['id']
            new_ids.add(event_id)
            normalized = normalize_resobin_event(item)

            obj, _ = ExternalCalendarEventCache.objects.update_or_create(
                user=user,
                provider='resobin',
                external_event_id=event_id,
                external_calendar_id='',
                defaults=normalized,
            )
            changed_months.add(normalized['start_time'].strftime('%Y-%m'))

            schedule_reminder(
                event_uid=f'resobin:{normalized["subsource"]}:{event_id}',
                user_id=str(user_id),
                start_time=normalized['start_time'],
                title=normalized['title'],
                source='resobin',
            )

        # Mark deletions
        deleted_ids = old_ids - new_ids
        if deleted_ids:
            ExternalCalendarEventCache.objects.filter(
                user=user,
                provider='resobin',
                external_event_id__in=deleted_ids,
            ).update(is_cancelled=True)
            for eid in deleted_ids:
                cancel_reminder_by_external_id(str(user_id), eid)

        # Invalidate Redis window cache for affected months
        try:
            pipe = redis_client.pipeline()
            for month in changed_months:
                pipe.delete(f'calendar:user:{user_id}:window:{month}')
            pipe.setex(f'calendar:user:{user_id}:source:resobin:fresh', 1800, '1')
            pipe.execute()
        except Exception:
            pass

        account.status = ExternalCalendarAccount.Status.ACTIVE
        account.last_sync_at = now()
        account.last_sync_status = 'success'
        account.last_sync_error = ''
        account.save(update_fields=['status', 'last_sync_at', 'last_sync_status', 'last_sync_error'])

    except ResoBinAPIError as exc:
        if account is not None:
            account.status = ExternalCalendarAccount.Status.ERROR
            account.last_sync_error = str(exc)
            account.save(update_fields=['status', 'last_sync_error'])
        raise self.retry(exc=exc)

    finally:
        try:
            redis_client.delete(lock_key)
        except Exception:
            pass
