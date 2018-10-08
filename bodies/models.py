"""Models for Body and their children (BodyChildRelation)."""
from uuid import uuid4
from django.db import models
from helpers.misc import get_url_friendly

class Body(models.Model):
    """An organization or club which may conduct events."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    str_id = models.CharField(max_length=50, editable=False, null=True)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    time_of_modification = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=50)
    canonical_name = models.CharField(max_length=50, blank=True)
    short_description = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    website_url = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    cover_url = models.URLField(blank=True, null=True)
    blog_url = models.URLField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.str_id = get_url_friendly(
            self.name if not self.canonical_name else self.canonical_name)
        super(Body, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/org/' + self.str_id

    class Meta:
        verbose_name = "Body"
        verbose_name_plural = "Bodies"
        ordering = ("name",)

class BodyChildRelation(models.Model):
    """Relates a body to one child."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    parent = models.ForeignKey(
        Body, on_delete=models.CASCADE, default=uuid4, related_name='children')
    child = models.ForeignKey(
        Body, on_delete=models.CASCADE, default=uuid4, related_name='parents')

    def __str__(self):
        return self.parent.name + " --> " + self.child.name

    class Meta:
        verbose_name = "Body-Child Relation"
        verbose_name_plural = "Body-Child Relations"
        ordering = ("parent__name",)
