from datetime import timedelta

from celery import shared_task
from django.utils.timezone import now


def schedule_reminder(event_uid, user_id, start_time, title, source):
    """Schedule a push notification 30 minutes before the event starts."""
    fire_at = start_time - timedelta(minutes=30)
    if fire_at <= now():
        return
    try:
        send_event_reminder.apply_async(
            args=[str(user_id), event_uid, title, source],
            eta=fire_at,
            task_id=f'reminder:{event_uid}:{user_id}',
        )
    except Exception:
        pass


def cancel_reminder(event_uid, user_id):
    """Revoke a scheduled reminder task."""
    try:
        from backend.celery import app
        app.control.revoke(f'reminder:{event_uid}:{user_id}')
    except Exception:
        pass


def cancel_reminder_by_external_id(user_id, external_event_id):
    """Revoke reminders for a resobin event across all possible subsources."""
    try:
        from backend.celery import app
        for subsource in ('class', 'tutorial', 'lab', 'exam', 'deadline', 'other'):
            app.control.revoke(f'reminder:resobin:{subsource}:{external_event_id}:{user_id}')
    except Exception:
        pass


@shared_task(bind=True, max_retries=3, queue='notifications')
def send_event_reminder(self, user_id, event_uid, title, source):
    """Send a 30-minute reminder push notification to the user."""
    from users.models import UserProfile
    from calendarhub.models import CalendarSourcePreference, ExternalCalendarEventCache
    from calendarhub.services.push import push_service

    try:
        user = UserProfile.objects.get(id=user_id)

        prefs = CalendarSourcePreference.objects.filter(user=user).first()
        if prefs and not prefs.notifications_enabled:
            return

        # For resobin events, verify the event hasn't been cancelled since scheduling
        if source == 'resobin':
            parts = event_uid.split(':')
            external_id = parts[2] if len(parts) >= 3 else None
            if external_id:
                exists = ExternalCalendarEventCache.objects.filter(
                    user=user,
                    provider='resobin',
                    external_event_id=external_id,
                    is_cancelled=False,
                ).exists()
                if not exists:
                    return

        push_service.send_to_user(user, {
            'title': 'Starting in 30 minutes',
            'body': title,
            'data': {
                'type': 'event_reminder',
                'event_uid': event_uid,
                'source': source,
            },
        })

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(queue='notifications')
def send_change_notification(user_id, change_type, title, detail=''):
    """Send an immediate push notification for a timetable change."""
    from users.models import UserProfile
    from calendarhub.models import CalendarSourcePreference
    from calendarhub.services.push import push_service

    NOTIFY_WORTHY = {
        'exam_added', 'exam_modified', 'exam_cancelled',
        'slot_cancelled', 'slot_modified', 'deadline_added',
    }
    if change_type not in NOTIFY_WORTHY:
        return

    MESSAGES = {
        'exam_added':     'New exam added',
        'exam_modified':  'Exam time or location changed',
        'exam_cancelled': 'Exam cancelled',
        'slot_cancelled': 'Class cancelled',
        'slot_modified':  'Class time or location changed',
        'deadline_added': 'New deadline added',
    }

    try:
        user = UserProfile.objects.get(id=user_id)
        prefs = CalendarSourcePreference.objects.filter(user=user).first()
        if prefs and not prefs.notifications_enabled:
            return
        push_service.send_to_user(user, {
            'title': MESSAGES[change_type],
            'body': title,
            'data': {'type': 'timetable_change', 'change_type': change_type},
        })
    except Exception:
        pass
