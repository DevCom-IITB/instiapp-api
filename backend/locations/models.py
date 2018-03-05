' Models for Locations '
from uuid import uuid4
from django.db import models

class Location(models.Model):
    '''
    A unique location on the campus, chiefly venues for events

    Attributes:
        `lat` - Latitude
        'lng` - Longitude
    '''

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return self.name
