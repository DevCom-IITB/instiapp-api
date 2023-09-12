from django.db import models
from messmenu.models import Hostel
from uuid import uuid4


class GC(models.Model):
    TYPE_CHOICES = (
        (1, "Tech"),
        (2, "Sports"),
        (3, "Cultural"),
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50)
    type = models.PositiveIntegerField(choices=TYPE_CHOICES)

    def __str__(self):
        return self.name


class GC_Hostel_Points(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    gc = models.ForeignKey(GC, on_delete=models.CASCADE)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        
        return self.hostel.short_name
