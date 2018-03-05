' Model for Body and children'
from uuid import uuid4
from django.db import models

class Body(models.Model):
    ' An organization or club which may conduct events '

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True)
    image_url = models.URLField(blank=True, null=True)
    events = models.ManyToManyField('events.Event', related_name='bodies', blank=True)

    def __str__(self):
        return self.name

    class Meta:
         verbose_name = "Body"
         verbose_name_plural = "Bodies"

class BodyChildRelation(models.Model):
    ' Relates a body to one child '

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    parent = models.ForeignKey(Body, on_delete=models.CASCADE, default=uuid4, related_name='children')
    child = models.ForeignKey(Body, on_delete=models.CASCADE, default=uuid4, related_name='parents')

    def __str__(self):
        return self.parent.name + " --> " + self.child.name

    class Meta:
         verbose_name = "Body-Child Relation"
         verbose_name_plural = "Body-Child Relations"