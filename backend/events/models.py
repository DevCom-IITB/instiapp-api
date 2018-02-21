from django.db import models
from uuid import uuid4
from users.models import UserProfile
from locations.models import Location

# Create your models here.
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    image_url = models.URLField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    # created_by : User
    all_day = models.BooleanField(default=False)
    venue = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)

    followers = models.ManyToManyField(
        UserProfile,
        through='UserEventStatus',
        through_fields=('event', 'user'),
        blank=True
    )
    # body : Body

    def __str__(self):
        return self.name

class UserEventStatus(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)

    # Cascading on delete is delibrate here, since the entry
    # makes no sense if the user or event gets deleted
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, default=uuid4)

    event = models.ForeignKey(Event, on_delete=models.CASCADE, default=uuid4)

    # Probability of attending the event
    status = models.IntegerField(default=0)