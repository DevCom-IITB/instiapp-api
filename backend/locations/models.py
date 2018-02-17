from django.db import models

class Location(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=50)
    lat = models.CharField(max_length=50)
    lng = models.CharField(max_length=50)