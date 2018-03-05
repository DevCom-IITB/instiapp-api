' Models for Event and UserEventStatus '
from uuid import uuid4
from django.db import models

class Event(models.Model):
    '''
    An event to be associated with one or more Bodies

    Attributes:
        `followers` - relates multiple `UserEventStatus` for the Event
    '''

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True)
    image_url = models.URLField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey('users.UserProfile', null=True, blank=True, on_delete=models.SET_NULL)
    all_day = models.BooleanField(default=False)
    venues = models.ManyToManyField('locations.Location', related_name='events', blank=True)

    def __str__(self):
        return self.name

    class Meta:
         verbose_name = "Event"
         verbose_name_plural = "Events"

class UserEventStatus(models.Model):
    '''
    Associates a User and an Event, describing probabilty of attending

    Attributes:
        `status` - probability of attending the event,
        e.g. 0 - not going, 1 - interested, 2 - going etc.
    '''

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)

    # Cascading on delete is delibrate here, since the entry
    # makes no sense if the user or event gets deleted
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, default=uuid4, related_name='events_followed')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, default=uuid4, related_name='user_event_statuses')

    status = models.IntegerField(default=0)

    class Meta:
         verbose_name = "User-Event Status"
         verbose_name_plural = "User-Event Statuses"
