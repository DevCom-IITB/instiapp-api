"""Models for Locations."""
from uuid import uuid4
from django.db import models
from helpers.misc import get_url_friendly
from locations.management.commands.Addloc import add_conns, delete_connections
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
    connected_locs = models.TextField(blank=True, null=True)
    adjacent_locs = models.ManyToManyField(
        'locations.Location', through='LocationLocationDistance',
        related_name='adjacent_loc', blank=True)

    def save(self, *args, **kwargs):        # pylint: disable =W0222
        self.str_id = get_url_friendly(self.short_name)
        adj_data = self.connected_locs
        if adj_data:
            locs = adj_data.split(',')
            for loc in locs:
                if loc:
                    loc = Location.objects.filter(name=loc).first()
                    add_conns(self, loc)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        delete_connections(self)
        super().delete(*args, **kwargs)


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

class LocationLocationDistance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    location1 = models.ForeignKey(Location, on_delete=models.CASCADE,
                                  default=uuid4, related_name='lld1')
    location2 = models.ForeignKey(Location, on_delete=models.CASCADE,
                                  default=uuid4, related_name='lld2')
    distance = models.FloatField(default=100000000)

    class Meta:
        verbose_name = "Location-Location Distance"
        verbose_name_plural = "Location-Location Distances"
