"""Models for Event and UserEventStatus."""
from uuid import uuid4
from django.db import models
from helpers.misc import get_url_friendly

class Event(models.Model):
    """An event to be associated with one or more Bodies.

    Attributes:
        `followers` - relates multiple `UserEventStatus` for the Event.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    str_id = models.CharField(max_length=58, editable=False, null=True)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    time_of_modification = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    bodies = models.ManyToManyField('bodies.Body', related_name='events', blank=True)
    image_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey('users.UserProfile', null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='created_events')
    all_day = models.BooleanField(default=False)
    venues = models.ManyToManyField('locations.Location', related_name='events', blank=True)
    followers = models.ManyToManyField('users.UserProfile', through='UserEventStatus',
                                       related_name='followed_events', blank=True)

    archived = models.BooleanField(default=False)
    notify = models.BooleanField(default=True)
    user_tags = models.ManyToManyField('users.UserTag', related_name='events', blank=True)

    starting_notified = models.BooleanField(default=False)

    promotion_boost = models.IntegerField(default=0)

    weight = 0

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.str_id = get_url_friendly(self.name) + "-" + str(self.id)[:8]
        super(Event, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '/event/' + self.str_id

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ("-start_time",)
        indexes = [
            models.Index(fields=['start_time', ]),
        ]

class UserEventStatus(models.Model):
    """Associates a User and an Event, describing probabilty of attending.

    Attributes:
        `status` - probability of attending the event,
        e.g. 0 - not going, 1 - interested, 2 - going etc.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)

    # Cascading on delete is delibrate here, since the entry
    # makes no sense if the user or event gets deleted
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE,
                             default=uuid4, related_name='ues')
    event = models.ForeignKey(Event, on_delete=models.CASCADE,
                              default=uuid4, related_name='ues')

    status = models.IntegerField(default=0)

    class Meta:
        verbose_name = "User-Event Status"
        verbose_name_plural = "User-Event Statuses"
