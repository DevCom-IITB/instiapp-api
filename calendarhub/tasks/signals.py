# from django.db.models.signals import post_save
from django.dispatch import receiver,Signal
from calendarhub.models import SharedCalendar, UserSharedCalendarSubscription

creater_approved=Signal()

@receiver(creater_approved)
def subscribe_all_users_to_new_public_calendar(sender, instance, created, **kwargs):
    """
    When a new public and active SharedCalendar is created,
    subscribe all existing users to it by default.
    """
    if created and instance.is_public and instance.is_active:
        from users.models import UserProfile

        users_to_subscribe = UserProfile.objects.all()

        subscriptions = [
            UserSharedCalendarSubscription(user=user, calendar=instance)
            for user in users_to_subscribe
        ]

        UserSharedCalendarSubscription.objects.bulk_create(subscriptions, ignore_conflicts=True)