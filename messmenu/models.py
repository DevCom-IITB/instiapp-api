"""Mess menu models."""
from uuid import uuid4
from django.db import models

class Hostel(models.Model):
    """Entry for each hostel."""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=40, blank=True)

class MenuEntry(models.Model):
    """Menu entries for a single day-hostel pair."""
    # Meta
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='mess')
    day = models.IntegerField()

    # Menu
    breakfast = models.TextField(blank=True)
    lunch = models.TextField(blank=True)
    snacks = models.TextField(blank=True)
    dinner = models.TextField(blank=True)
