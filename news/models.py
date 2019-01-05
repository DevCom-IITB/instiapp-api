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
    notify = models.BooleanField(default=True)
    reacted_by = models.ManyToManyField(
        'users.UserProfile', through='UserNewsReaction',
        related_name='news_reactions', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "News Entry"
        verbose_name_plural = "News Entries"
        ordering = ("-published",)
        indexes = [
            models.Index(fields=['guid', ]),
        ]

class UserNewsReaction(models.Model):
    """ Reaction:
            0 - Like
            1 - Love
            2 - Haha
            3 - Wow
            4 - Sad
            5 - Angry
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE,
                             default=uuid4, related_name='unr')
    news = models.ForeignKey(NewsEntry, on_delete=models.CASCADE,
                             default=uuid4, related_name='unr')

    reaction = models.IntegerField(default=0)

    class Meta:
        verbose_name = "User-News Reaction"
        verbose_name_plural = "User-News Reactions"
