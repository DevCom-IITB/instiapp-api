from datetime import datetime
from uuid import uuid4
from django.db import models
from helpers.misc import get_url_friendly


class Community(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    str_id = models.CharField(max_length=58, editable=False, null=True)
    name = models.CharField(max_length=100)
    about = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    logo_image = models.URLField(blank=True, null=True)
    cover_image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    body = models.ForeignKey(
        "bodies.Body", on_delete=models.CASCADE, related_name="community_body"
    )
    followers = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):  # pylint: disable=W0222
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
    content = models.TextField(null=True, blank=True)
    image_url = models.TextField(blank=True, null=True)
    
    reported_by = models.ManyToManyField(
        "users.UserProfile", related_name="posts_reported", blank=True
    )
    reacted_by = models.ManyToManyField(
        "users.UserProfile",
        through="CommunityPostUserReaction",
        related_name="communitypost_reaction",
        blank=True,
    )
    featured = models.BooleanField(default=False, null=True, blank=True)
    deleted = models.BooleanField(default=False, null=True, blank=True)
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name="posts"
    )
    ignored = models.BooleanField(default=False, null=True, blank=True)
    thread_rank = models.IntegerField(default=1, null=True, blank=True)
    parent = models.ForeignKey(
        "self", blank=True, null=True, related_name="comments", on_delete=models.CASCADE
    )
    ispoll = models.BooleanField(default=False)

    # comments = models.ManyToManyField(
    #     "self", blank=True, related_name="community_post_comments")

    tag_user = models.ManyToManyField(
        "users.UserProfile", related_name="taggedcommunitypost", blank=True
    )
    tag_body = models.ManyToManyField(
        "bodies.Body", related_name="taggedcommunityposts", blank=True
    )
    tag_location = models.ManyToManyField(
        "locations.Location", related_name="taggedcommunityposts", blank=True
    )
    followed_by = models.ManyToManyField(
        "users.UserProfile", related_name="followedposts", blank=True
    )
    anonymous = models.BooleanField(default=False, blank=True)
    posted_by = models.ForeignKey(
        "users.UserProfile", on_delete=models.CASCADE, related_name="communityposts"
    )
    interests = models.ManyToManyField(
        "achievements.Interest", related_name="communitypost_interest", blank=True
    )

    """ Status
        0 - Pending
        1 - Approved
        2 - Rejected
        3 - Reported

    """
    status = models.IntegerField(null=True, blank=True, default=0)

    def save(self, *args, **kwargs):  # pylint: disable=W0222
        self.str_id = get_url_friendly(str(datetime.now())) + "-" + str(self.id)[:8]
        if not self.ignored:
            if self.reported_by.count() > 1:
                self.status = 3
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.content[:100]

    class Meta:
        verbose_name = "Community Post"
        verbose_name_plural = "Community Posts"
        ordering = ("-time_of_creation",)


class CommunityPostUserReaction(models.Model):
    """Reaction:
    0 - Like
    1 - Love
    2 - Haha
    3 - Wow
    4 - Sad
    5 - Angry
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        "users.UserProfile", on_delete=models.CASCADE, related_name="ucpr"
    )
    communitypost = models.ForeignKey(
        CommunityPost, on_delete=models.CASCADE, related_name="ucpr"
    )
    reaction = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Community Post User Reaction"
        verbose_name_plural = "Community Post User Reactions"


class Poll(models.Model):
    """Separate poll model linked to community post"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    community_post = models.OneToOneField(CommunityPost, on_delete=models.CASCADE, related_name='poll')
    question = models.TextField()
    allow_multiple_answers = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Poll: {self.question[:50]}"
    
class PollOption(models.Model):
    """Poll options"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    vote_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['poll', 'order']

class PollVote(models.Model):
    """User votes on poll options"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['poll', 'user', 'option']  # Prevent duplicate votes (unless multiple answers allowed)

    # def save(self, *args, **kwargs):
    #     # Check if multiple answers are allowed
    #     if not self.poll.allow_multiple_answers:
    #         # Delete any existing votes by this user for this poll
    #         PollVote.objects.filter(poll=self.poll, user=self.user).delete()
        
    #     super().save(*args, **kwargs)
        
    #     # Update vote count
    #     self.option.vote_count = self.option.votes.count()
    #     self.option.save()

    