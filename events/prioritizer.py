"""Event prioritizer."""
import math
from datetime import timedelta
from django.utils import timezone
from events.serializers import EventSerializer

BASE = 1000                              # Base points
FINISHED_PENALTY = 600                   # Direct penalty if event is done
WEIGHT_START_TIME = 800                  # Weight of time from event start
WEIGHT_END_TIME = 800                    # Weight of time from event end
TIME_SD = 2.5                            # Standard deviation of time distribution
TIME_L_END = 1.2                         # Lambda for exponential of ended penalty
BODY_FOLLOWING_BONUS = 100               # Bonus if the body is followed
TIME_DEP_BODY_BONUS = 200                # Bonus if the body is followed dependent on time
BODY_BONUS_MAX = 400                     # Maximum bonus for followed bodies

def get_prioritized(queryset, request):
    now = timezone.now()

    # Prefetch related
    queryset = EventSerializer.setup_eager_loading(queryset)

    # Prefetch followed bodies
    followed_bodies = None
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        profile = request.user.profile
        followed_bodies = profile.followed_bodies.all()

    # Iterate all events
    for event in queryset:
        event.weight = BASE

        # Get difference in days
        end_time_diff = (event.end_time - now).total_seconds() / 86400
        start_time_diff = (event.start_time - now).total_seconds()  / 86400

        start_time_factor = math.exp((-(start_time_diff / TIME_SD)**2))

        # Apply exponential to and penalise finished events
        if event.end_time < now:
            event.weight -= FINISHED_PENALTY
            end_time_factor = math.exp(-abs(end_time_diff) / TIME_L_END)
            start_time_factor *= end_time_factor

        start_time_points = WEIGHT_START_TIME * start_time_factor
        event.weight += int(start_time_points)

        if followed_bodies:
            body_bonus = 0
            for body in event.bodies.all():
                if body_bonus >= BODY_BONUS_MAX:
                    break
                if body in followed_bodies:
                    body_bonus += int(BODY_FOLLOWING_BONUS + (TIME_DEP_BODY_BONUS * start_time_factor))
            event.weight += body_bonus

    return sorted(queryset, key=lambda event: (-event.weight, event.start_time))

def get_fresh_events(queryset, delta=3):
    """Gets events after removing stale ones."""
    return queryset.filter(
        archived=False, end_time__gte=timezone.now() - timedelta(days=delta))

def get_fresh_prioritized_events(queryset, request):
    """Gets fresh events with prioritization."""
    return get_prioritized(get_fresh_events(queryset), request)

def get_r_fresh_prioritized_events(queryset, request):
    """Get relatively fresh events with prioritization. Very old events are removed."""
    return get_prioritized(get_fresh_events(queryset, 30), request)
