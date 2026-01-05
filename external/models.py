"""Models for external opportunities."""
from uuid import uuid4
from django.db import models
from django.utils.timezone import now


class ExternalBlogEntry(models.Model):
    """A single entry on the external blog."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    guid = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=300, blank=True)
    content = models.TextField(blank=True)
    link = models.CharField(max_length=200, blank=True)
    published = models.DateTimeField(default=now)
    body = models.TextField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.title} - {self.body}"

    class Meta:
        verbose_name = "External Blog Entry"
        verbose_name_plural = "External Blog Entries"
        ordering = ("-published",)
        indexes = [
            models.Index(
                fields=[
                    "guid",
                ]
            ),
        ]
