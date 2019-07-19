"""Models for the achievements API."""
from uuid import uuid4
from django.db import models

class Achievement(models.Model):
    """A single achievement that *may or may not be verified*"""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    time_of_modification = models.DateTimeField(auto_now=True)

    user = models.ForeignKey('users.UserProfile', null=False,
                             on_delete=models.CASCADE, related_name='achievements')

    dismissed = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey('users.UserProfile', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='achievements_verified_by')

    title = models.CharField(max_length=80)
    description = models.TextField(blank=True, null=True)
    admin_note = models.TextField(blank=True, null=True)

    body = models.ForeignKey('bodies.Body', null=True,
                             on_delete=models.SET_NULL, related_name='achievements')

    event = models.ForeignKey('events.Event', null=True,
                              on_delete=models.SET_NULL, related_name='achievements')

    class Meta:
        ordering = ("-time_of_creation",)
