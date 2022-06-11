from uuid import uuid4
from django.db import models
from helpers.misc import get_url_friendly

class IDF_Post_Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    content = models.TextField(blank=True,null=True)
    image_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    reaction = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    threadRank = models.IntegerField(default=1)
    comments = models.ForeignKey("self", null=True, related_name="IDF_Post_Comment")
    gif = models.FileField(upload_to = 'Videos/', blank = True)
    tag_checkIn = models.URLField(blank=True, null=True)

