"""Models for Event and UserEventStatus."""
from uuid import uuid4
from django.db import models
from helpers.misc import get_url_friendly
from multiselectfield import MultiSelectField

# production
COUNCIL_IDS = (
    ("91199c20-7488-41c5-9f6b-6f6c7c5b897d", "Institute Cultural Council"),
    ("81e05a1a-7fd1-45b5-84f6-074e52c0f085", "Institute Technical Council"),
    ("a9f81e69-fcc9-4fe3-b261-9e5e7a13f898", "Institute Sports Council"),
    ("f3ae5230-4441-4586-81a8-bf75a2e47318", "Hostel Affairs"),
)

# COUNCIL_IDS = (
#     ("d920d898-0998-4ed9-8fb8-f270310b2bec", "Institute Cultural Council"),
#     ("ae084ebb-6009-4095-a774-44ad0f107bc0", "Institute Technical Council"),
#     ("0aa10bcc-f08f-44c6-bf50-1ce9b5c2f0f0", "Institute Sports Council"),
#     ("6c43632e-de1f-4088-8e77-60af60139e91", "Hostel Affairs"),
# )


class Event(models.Model):
    """An event to be associated with one or more Bodies.

    Attributes:
        `followers` - relates multiple `UserEventStatus` for the Event.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    str_id = models.CharField(max_length=58, editable=False, null=True)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    time_of_modification = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=60)
    description = models.TextField(blank=True)
    longdescription = models.TextField(default='')
    email_verified = models.BooleanField(default=False)
    verification_body = MultiSelectField(choices=COUNCIL_IDS)
    bodies = models.ManyToManyField("bodies.Body", related_name="events", blank=True)
    image_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(
        "users.UserProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_events",
    )
    all_day = models.BooleanField(default=False)
    venues = models.ManyToManyField(
        "locations.Location", related_name="events", blank=True
    )
    followers = models.ManyToManyField(
        "users.UserProfile",
        through="UserEventStatus",
        related_name="followed_events",
        blank=True,
    )

    archived = models.BooleanField(default=False)
    notify = models.BooleanField(default=True)
    user_tags = models.ManyToManyField(
        "users.UserTag", related_name="events", blank=True
    )

    starting_notified = models.BooleanField(default=False)

    event_interest = models.ManyToManyField(
        "achievements.Interest", related_name="events", blank=True
    )

    promotion_boost = models.IntegerField(default=0)

    weight = 0

    def __str__(self):
        all_bodies = self.all_bodies()
        if all_bodies == []:
            return self.name
        bodies_str = all_bodies[0]
        for body in all_bodies[1:]:
            bodies_str += ", " + body
        return f"{self.name} - {bodies_str}"

    def save(self, *args, **kwargs):  # pylint: disable=W0222
        self.str_id = get_url_friendly(self.name) + "-" + str(self.id)[:8]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return "/event/" + self.str_id

    def all_bodies(self):
        return [str(body) for body in self.bodies.all()]
    
    def get_verification_body_id(self):
        for key, name in COUNCIL_IDS :
            if name == str(self.verification_body): 
                return key
        return

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ("-start_time",)
        indexes = [
            models.Index(
                fields=[
                    "start_time",
                ]
            ),
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
    user = models.ForeignKey(
        "users.UserProfile", on_delete=models.CASCADE, default=uuid4, related_name="ues"
    )
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, default=uuid4, related_name="ues"
    )

    status = models.IntegerField(default=0)

    class Meta:
        verbose_name = "User-Event Status"
        verbose_name_plural = "User-Event Statuses"
