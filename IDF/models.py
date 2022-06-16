from pyexpat import model
from uuid import uuid4
from django.db import models
from helpers.misc import get_url_friendly

class IDF_Post_Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    content = models.TextField(blank=True,null=True)
    image_url = models.URLField(blank=True, null=True)# also include gif for it
    website_url = models.URLField(blank=True, null=True)
    reacted_by = models.ManyToManyField(
        'users.UserProfile', through='UserReaction',
        related_name='reactions', blank=True)
    likes = models.IntegerField(default=0)
    threadRank = models.IntegerField(default=1)#this defines the thread rank ok so if you dont understand by the terminology this defines the rank of the post or comment like a post has T.R. 1 a comment made directly on the post has T.R. 2 a comment on that comment has thread rank 3
    comments = models.ManyToManyField("self", null=True, related_name="IDF_Post_Comment")
    tag_user = models.ManyToManyField("users.UserProfile", related_name="Tagged_user",blank=True)
    tag_location = models.ManyToManyField('locations.Location', related_name='IDF-TAGGED-LOCALE', blank=True)
    posted_by = models.ForeignKey('users.UserProfile', null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='created_events')
    tag_body = models.ManyToManyField('bodies.Body', related_name="Tagged_Body", blank=True)
    notify=models.BooleanField(default=True)
    #if we are going to user the users.UserTag to tag the user then i will also create a class in events for event tag

class UserReaction(models.Model):
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
    news = models.ForeignKey(IDF_Post_Comment, on_delete=models.CASCADE,
                             default=uuid4, related_name='unr')

    reaction = models.IntegerField(default=0)

    class Meta:
        verbose_name = "User Reaction"
        verbose_name_plural = "User Reactions"
