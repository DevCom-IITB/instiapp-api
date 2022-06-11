from uuid import uuid4
from django.db import models
from helpers.misc import get_url_friendly

class IDF_Post_Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    content = models.TextField(blank=True,null=True)
    image_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    reacted_by = models.ManyToManyField(
        'users.UserProfile', through='UserNewsReaction',
        related_name='news_reactions', blank=True)
    likes = models.IntegerField(default=0)
    threadRank = models.IntegerField(default=1)
    comments = models.ForeignKey("self", null=True, related_name="IDF_Post_Comment")
    gif = models.FileField(upload_to = 'Videos/', blank = True)
    tag_checkIn = models.URLField(blank=True, null=True)

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
