from calendar import monthrange
from datetime import datetime, timedelta, timezone

from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_aware

from calendarhub.models import (
    ExternalCalendarEventCache,
    UserSharedCalendarSubscription,
    SharedCalendarEvent,
)

IST = timezone(timedelta(hours=5, minutes=30))


def month_bounds(month_str):
    """Return (start, end) aware datetimes for a 'YYYY-MM' string."""
    year, mon = int(month_str[:4]), int(month_str[5:7])
    _, last_day = monthrange(year, mon)
    start = make_aware(datetime(year, mon, 1, 0, 0, 0))
    end   = make_aware(datetime(year, mon, last_day, 23, 59, 59))
    return start, end


def _fmt(dt):
    if not is_aware(dt):
        dt = make_aware(dt)
    return dt.astimezone(IST).isoformat()


def normalize_instiapp_event(event, subsource):
    """Convert an Event instance to a unified feed dict."""
    return {
        'uid':          f'instiapp:{subsource}:{event.id}',
        'source':       'instiapp',
        'subsource':    subsource,
        'title':        event.name,
        'description':  event.description or '',
        'location':     event.venue_room or '',
        'start_time':   _fmt(event.start_time),
        'end_time':     _fmt(event.end_time),
        'all_day':      event.all_day,
        'event_id':     str(event.id),
        'event_str_id': event.str_id,
        'body_ids':     [str(b.id) for b in event.bodies.all()],
        'event_url':    event.website_url,
        'color_hint':   None,
    }


def get_resobin_events(user, month):
    """Return resobin feed dicts for the given month."""
    month_start, month_end = month_bounds(month)
    qs = ExternalCalendarEventCache.objects.filter(
        user=user,
        provider='resobin',
        start_time__lt=month_end,
        end_time__gt=month_start,
        is_cancelled=False,
    )
    return [{
        'uid':          f'resobin:{obj.subsource}:{obj.external_event_id}',
        'source':       'resobin',
        'subsource':    obj.subsource,
        'title':        obj.title,
        'description':  obj.description,
        'location':     obj.location,
        'start_time':   _fmt(obj.start_time),
        'end_time':     _fmt(obj.end_time),
        'all_day':      obj.all_day,
        'event_id':     None,
        'event_str_id': None,
        'body_ids':     None,
        'event_url':    obj.event_url,
        'color_hint':   None,
    } for obj in qs]


def get_shared_events(user, month):
    """Return shared calendar feed dicts for the given month."""
    cal_ids = list(
        UserSharedCalendarSubscription.objects
        .filter(user=user, enabled=True)
        .values_list('calendar_id', flat=True)
    )
    if not cal_ids:
        return []

    month_start, month_end = month_bounds(month)
    events = (
        SharedCalendarEvent.objects
        .filter(
            calendar_id__in=cal_ids,
            start_time__lt=month_end,
            end_time__gt=month_start,
            is_cancelled=False,
        )
        .select_related('calendar')
    )
    return [{
        'uid':          f'shared:{ev.calendar.slug}:{ev.id}',
        'source':       'shared',
        'subsource':    ev.calendar.slug,
        'title':        ev.title,
        'description':  ev.description,
        'location':     ev.location,
        'start_time':   _fmt(ev.start_time),
        'end_time':     _fmt(ev.end_time),
        'all_day':      ev.all_day,
        'event_id':     None,
        'event_str_id': None,
        'body_ids':     None,
        'event_url':    None,
        'color_hint':   ev.calendar.color,
    } for ev in events]


def overlaps(item, start, end):
    """Return True if event item falls within [start, end]."""
    from datetime import date
    item_start = parse_datetime(item['start_time'])
    item_end   = parse_datetime(item['end_time'])
    if item_start and not is_aware(item_start):
        item_start = make_aware(item_start)
    if item_end and not is_aware(item_end):
        item_end = make_aware(item_end)
    # Convert date to datetime if needed
    if isinstance(start, date) and not isinstance(start, datetime):
        start = make_aware(datetime(start.year, start.month, start.day, 0, 0, 0))
    if isinstance(end, date) and not isinstance(end, datetime):
        end = make_aware(datetime(end.year, end.month, end.day, 23, 59, 59))
    return item_start < end and item_end > start


def maybe_enqueue_resobin_sync(user):
    """Enqueue a ResoBin sync task if one is not already running. Returns True if enqueued."""
    from redis import Redis
    from django.conf import settings

    redis_client = Redis.from_url(getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'))
    lock_key = f'calendar:user:{user.id}:sync:resobin:lock'

    acquired = redis_client.set(lock_key, '1', nx=True, ex=60)
    if acquired:
        redis_client.delete(lock_key)
        from calendarhub.tasks.resobin_sync import sync_resobin_for_user
        sync_resobin_for_user.delay(str(user.id))
        return True
    return False


def dedupe_instiapp(items):
    seen   = {}
    result = []
    for item in items:
        if item['source'] != 'instiapp':
            result.append(item)
            continue
        key = item['event_id']
        if key in seen:
            existing = seen[key]
            if existing['subsource'] != item['subsource']:
                existing['subsource'] = 'going+followed_body'
        else:
            seen[key] = item
            result.append(item)
    return result
