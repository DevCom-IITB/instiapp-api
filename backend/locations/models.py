from django.db import models
from uuid import uuid4

class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name
