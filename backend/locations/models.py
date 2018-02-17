from django.db import models

class Location(models.Model):
    id = models.UUIDField(primary_key=True)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    lat = models.CharField(max_length=50)
    lng = models.CharField(max_length=50)

    def __str__(self):
        return self.name
