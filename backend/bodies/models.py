' Model for Body and children'
from uuid import uuid4
from django.db import models
from events.models import Event

class Body(models.Model):
    ' An organization or club which may conduct events '

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    image_url = models.URLField(blank=True, null=True)
    events = models.ManyToManyField(Event)

    def __str__(self):
        return self.name

class BodyChildRelation(models.Model):
    ' Relates a body to one child '

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    parent = models.ForeignKey(Body, on_delete=models.CASCADE, default=uuid4, related_name='children')
    child = models.ForeignKey(Body, on_delete=models.CASCADE, default=uuid4, related_name='parents')

    def __str__(self):
        return self.parent.name + " --> " + self.child.name
