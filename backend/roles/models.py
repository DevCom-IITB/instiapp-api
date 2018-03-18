"""Models for Roles, which define things a user can do."""
from uuid import uuid4
from django.db import models
from multiselectfield import MultiSelectField

PERMISSION_CHOICES = (
    ('AddE', 'Add Event'),
    ('UpdE', 'Update Event'),
    ('DelE', 'Delete Event'),
    ('UpdB', 'Update Body'),
)

class BodyRole(models.Model):
    """A role for a bodywhich can be granted to multiple users."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    body = models.ForeignKey('bodies.Body', on_delete=models.CASCADE)
    inheritable = models.BooleanField(default=False)
    permissions = MultiSelectField(choices=PERMISSION_CHOICES)

    class Meta:
        verbose_name = "Body Role"
        verbose_name_plural = "Body Roles"

    def __str__(self):
        return self.name