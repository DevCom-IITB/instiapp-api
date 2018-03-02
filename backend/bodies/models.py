' Model for Body '
from uuid import uuid4
from django.db import models

class Body(models.Model):
    ' An organization or club which may conduct events '

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    image_url = models.URLField()
