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
TIME_PENALTY_FACTOR = 0.05               # Multiplying factor for event length penalty
LINEAR_DECAY = 0.05                      # Slope of linear decay
FAR_OFF_THRESHOLD = 15                   # Time in days after which events are considered far off
NOT_TAG_TARGET_PENALTY = 2000            # Penalty if not targeted in a restricted event


class EventPrioritizer():  # pylint: disable=R0902
    """Sets the weight for one event."""

    def __init__(self, event, profile):
        self.event = event
        self.followed_bodies = profile.followed_bodies.all() if profile else None
        self.profile = profile

        # Get time differences in days
        now = timezone.now()
        self.end_time_diff = (event.end_time - now).total_seconds() / 86400
        self.start_time_diff = (event.start_time - now).total_seconds() / 86400
        self.event_length = (event.end_time - event.start_time).total_seconds() / 86400
        self.days_till_event = (event.start_time - now).total_seconds() / 86400

        self.start_time_factor = 1
        self.weight = BASE

    def compute(self):
        """Compute the weight for the event."""

        # Apply all bonuses/penalties
        self.apply_time_bonus()
        self.penalise_untagged()

        # Give bonuses to events yet to end
        if self.event.end_time > timezone.now():
            self.penalise_far_off()
            self.penalise_length()
            self.bonus_followed()
            self.bonus_promotion()

        return self

    def apply_time_bonus(self):
        """Apply bonus to events starting soon with normal."""
        self.start_time_factor = math.exp((-(self.start_time_diff / TIME_SD)**2))
        self.start_time_factor *= self.penalise_finished()
        self.weight += int(WEIGHT_START_TIME * self.start_time_factor)

    def penalise_finished(self):
        """Apply exponential to penalise finished events
        Get the factor to multiply time bonus if event ended and
        also apply static penalty if done."""

        if self.event.end_time < timezone.now():
            self.weight -= FINISHED_PENALTY
            return math.exp(-abs(self.end_time_diff) / TIME_L_END)
        return 1

    def penalise_untagged(self):
        """Penalize for not being tagged in restricted audience."""
        categories_satisfy = []
        categories = []
        for tag in self.event.user_tags.all():
            if tag.category not in categories:
                categories.append(tag.category)
            if tag.category not in categories_satisfy and tag.match(self.profile):
                categories_satisfy.append(tag.category)
        self.weight -= int((len(categories) - len(categories_satisfy)) * NOT_TAG_TARGET_PENALTY)

    def bonus_followed(self):
        """Apply bonus if user is following a body conducting the event."""
        if self.followed_bodies:
            body_bonus = 0
            for body in self.event.bodies.all():
                if body_bonus >= BODY_BONUS_MAX:
                    break
                if body in self.followed_bodies:
                    body_bonus += int(BODY_FOLLOWING_BONUS + (TIME_DEP_BODY_BONUS * self.start_time_factor))
            self.weight += body_bonus

    def penalise_far_off(self):
        """Penalise events that have a long time to start linearly."""
        if self.days_till_event > FAR_OFF_THRESHOLD:
            self.weight *= (1 - (self.days_till_event - FAR_OFF_THRESHOLD) * LINEAR_DECAY)

    def penalise_length(self):
        """Penalise long running events."""
        self.weight *= 1 / (1 + TIME_PENALTY_FACTOR * math.floor(self.event_length))

    def bonus_promotion(self):
        """Add bonus for promoted events"""
        self.weight += self.event.promotion_boost * self.start_time_factor


def get_prioritized(queryset, request):
    # Prefetch related
    queryset = EventSerializer.setup_eager_loading(queryset, request)

    # Get profile if authenticated
    profile = None
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        profile = request.user.profile

    # Iterate all events
    for event in queryset:
        event.weight = EventPrioritizer(event, profile).compute().weight

    return sorted(queryset, key=lambda event: (event.weight, event.start_time), reverse=True)

def get_fresh_events(queryset, delta=3):
    """Gets events after removing stale ones."""
    return queryset.filter(
        end_time__gte=timezone.now() - timedelta(days=delta))

def get_fresh_prioritized_events(queryset, request, delta=3):
    """Gets fresh events with prioritization."""
    return get_prioritized(get_fresh_events(queryset, delta=delta), request)
