from django.db import models
from locations.models import Location

# Create your models here.
class Event(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    image_url = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    # created_by : User
    all_day = models.BooleanField(default=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    # body : Body

    def __str__(self):
        return self.name
