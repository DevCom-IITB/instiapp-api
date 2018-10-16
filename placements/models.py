"""Models for placements."""
from uuid import uuid4
from django.db import models
from django.utils.timezone import now

class BlogEntry(models.Model):
    """A single entry on the placements blog."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    guid = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=300, blank=True)
    content = models.TextField(blank=True)
    link = models.CharField(max_length=200, blank=True)
    published = models.DateTimeField(default=now)
    blog_url = models.URLField(null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Placement Blog Entry"
        verbose_name_plural = "Placement Blog Entries"
        ordering = ("-published",)
        indexes = [
            models.Index(fields=['guid', ]),
        ]
