from datetime import datetime
from pyexpat import model
from uuid import uuid4
from django.db import models
from helpers.misc import get_url_friendly

class Community(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    str_id = models.CharField(max_length=58, editable=False, null=True)
    name = models.CharField(max_length=100)
    about = models.TextField()
    description = models.TextField()
    logo_image = models.URLField(blank=True, null=True)
    cover_image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    body = models.ForeignKey('bodies.Body', on_delete=models.CASCADE, related_name='community_body', null=True)
    followers = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):        # pylint: disable=W0222
        self.str_id = get_url_friendly(self.name) + "-" + str(self.id)[:8]
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Community"
        verbose_name_plural = "Communities"
        ordering = ("-created_at",)

class CommunityPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    str_id = models.CharField(max_length=58, editable=False, null=True)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    time_of_modification = models.DateTimeField(auto_now=True)
    content = models.TextField(blank=True)
    image_url = models.TextField(blank=True, null=True)
    reported_by=models.ManyToManyField('users.UserProfile', related_name='posts_reported', blank=True)
    reacted_by = models.ManyToManyField(
        'users.UserProfile', through='CommunityPostUserReaction',
        related_name='communitypost_reaction', blank=True)
    view_count = models.IntegerField(default=0)
    featured = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)

    thread_rank = models.IntegerField(default=1, null=True)
    parent = models.ForeignKey("self", blank=True, null=True,
                               related_name="comments", on_delete=models.CASCADE)
    # comments = models.ManyToManyField(
    #     "self", blank=True, related_name="community_post_comments")

    tag_user = models.ManyToManyField("users.UserProfile", related_name="communitypost_taguser", blank=True)
    tag_body = models.ManyToManyField('bodies.Body', related_name="Tagged_Body", blank=True)
    tag_location = models.ManyToManyField('locations.Location', related_name='communitypost_tagloc', blank=True)
    followed_by = models.ManyToManyField("users.UserProfile", related_name="communitypost_followers", blank=True)
    anonymous = models.BooleanField(default=False,blank=True)
    posted_by = models.ForeignKey('users.UserProfile', null=True, blank=True,
                                  on_delete=models.SET_NULL, related_name='communitypost_postedby')
    interests = models.ManyToManyField('achievements.Interest', related_name='communitypost_interest', blank=True)

    """ Status
        0 - Pending
        1 - Approved
        2 - Rejected
        3 - Reported
        
    """
    status = models.IntegerField(null=True, blank=True, default=0)

    def save(self, *args, **kwargs):        # pylint: disable=W0222
        self.str_id = get_url_friendly(str(datetime.now())) + "-" + str(self.id)[:8]
        super().save(*args, **kwargs)
        # communitypost = CommunityPost.objects.get(id=self.id)
        # communitypost.reports = communitypost.reported_by.count
        
    def __str__(self) -> str:
        return self.content[:100]

    class Meta:
        verbose_name = "Community Post"
        verbose_name_plural = "Community Posts"
        ordering = ("-time_of_creation",)

class CommunityPostUserReaction(models.Model):
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
                             default=uuid4, related_name='ucpr')
    communitypost = models.ForeignKey(CommunityPost, on_delete=models.CASCADE,
                                      default=uuid4, related_name='ucpr')
    reaction = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Community Post User Reaction"
        verbose_name_plural = "Community Post User Reactions"
