"""Models for Locations."""
from uuid import uuid4
from django.db import models
from helpers.misc import get_url_friendly

class Location(models.Model):
    """A unique location, chiefly venues for events.

    Attributes:
        `lat` - Latitude
        'lng` - Longitude
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    str_id = models.CharField(max_length=100, editable=False, null=True)
    time_of_creation = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=80, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    parent_relation = models.CharField(max_length=50, blank=True, null=True)
    group_id = models.IntegerField(blank=True, null=True)

    pixel_x = models.IntegerField(blank=True, null=True)
    pixel_y = models.IntegerField(blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    reusable = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.str_id = get_url_friendly(self.short_name)
        super(Location, self).save(*args, **kwargs)

    def __str__(self):
        return (self.short_name if self.short_name else '') + ' - ' + self.name

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ("name",)
        indexes = [
            models.Index(fields=['reusable', ]),
            models.Index(fields=['reusable', 'group_id']),
        ]
