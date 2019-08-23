"""Models for the achievements API."""
from uuid import uuid4
import pyotp
from django.db import models
from django.db.models.signals import post_save

class OfferedAchievement(models.Model):
    """A single achievement offered by an event."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    time_of_modification = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=80)
    description = models.TextField(blank=True, default="")
    priority = models.IntegerField(default=0)
    generic = models.CharField(max_length=20, default="generic")

    body = models.ForeignKey('bodies.Body', on_delete=models.CASCADE,
                             related_name='offered_achievements')

    event = models.ForeignKey('events.Event', on_delete=models.CASCADE,
                              related_name='offered_achievements')

    secret = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ("priority",)

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):  # pylint: disable=unused-argument
        if created:
            instance.secret = pyotp.random_base32()
            instance.save()


class Achievement(models.Model):
    """A single achievement that *may or may not be verified*"""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    time_of_modification = models.DateTimeField(auto_now=True)

    user = models.ForeignKey('users.UserProfile', null=False,
                             on_delete=models.CASCADE, related_name='achievements')

    hidden = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey('users.UserProfile', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='achievements_verified_by')

    title = models.CharField(max_length=80)
    description = models.TextField(blank=True, default="")
    admin_note = models.TextField(blank=True, null=True)

    body = models.ForeignKey('bodies.Body', null=True,
                             on_delete=models.SET_NULL, related_name='achievements')

    event = models.ForeignKey('events.Event', null=True,
                              on_delete=models.SET_NULL, related_name='achievements')

    offer = models.ForeignKey(OfferedAchievement, null=True,
                              on_delete=models.SET_NULL, related_name='achievements')

    class Meta:
        ordering = ("-time_of_creation",)


post_save.connect(OfferedAchievement.post_create, sender=OfferedAchievement)
