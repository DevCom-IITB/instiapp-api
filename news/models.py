"""Models for news feed."""
from uuid import uuid4
from django.db import models
from django.utils.timezone import now
from bodies.models import Body

class NewsEntry(models.Model):
    """A single entry on a news blog."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    body = models.ForeignKey(Body, on_delete=models.CASCADE)
    guid = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=300, blank=True)
    content = models.TextField(blank=True)
    link = models.CharField(max_length=200, blank=True)
    published = models.DateTimeField(default=now)
    blog_url = models.URLField(null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "News Entry"
        verbose_name_plural = "News Entries"
        ordering = ("-published",)
