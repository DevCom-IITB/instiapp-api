"""Event prioritizer."""
from django.utils import timezone
import math

BASE = 1000                              # Base points
FINISHED_PENALTY = 900                   # Direct penalty if event is done
WEIGHT_START_TIME = 800                  # Weight of time from event start
WEIGHT_END_TIME = 800                    # Weight of time from event end
TIME_SD = 2.5                            # Standard deviation of time distribution
TIME_L_END = 1.2                         # Lambda for exponential of ended penalty
BODY_FOLLOWING_BONUS = 500               # Bonus if the body is followed

def get_prioritized(queryset, profile):
    now = timezone.now()

    print("")
    for event in queryset:
        event.weight = BASE

        # Get difference in days
        end_time_diff = (event.end_time - now).total_seconds() / 86400
        start_time_diff = (event.start_time - now).total_seconds()  / 86400

        start_time_factor = math.exp((-(start_time_diff / TIME_SD)**2))
        start_time_points = WEIGHT_START_TIME * start_time_factor

        # Apply exponential to and penalise finished events
        if event.end_time < now:
            event.weight -= FINISHED_PENALTY
            end_time_factor = math.exp(-abs(end_time_diff) / TIME_L_END)
            start_time_points *= end_time_factor

        event.weight += int(start_time_points)

        for body in event.bodies.all():
            if body in profile.followed_bodies.all():
                event.weight += int(BODY_FOLLOWING_BONUS * start_time_factor)

        print(event.name, event.weight, event.start_time)

    print("")

    return sorted(queryset, key=lambda event: event.weight, reverse=True)
