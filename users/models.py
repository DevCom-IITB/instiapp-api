"""Model for UserProfile."""
from __future__ import unicode_literals
import re
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User

TAG_TARGET_CHOICES = (
    ('roll_no', 'Roll No'),
    ('department', 'Department'),
    ('degree', 'Degree'),
    ('join_year', 'Join Year'),
    ('graduation_year', 'Graduation Year'),
    ('hostel', 'Hostel'),
    ('room', 'Room'),
    ('android_version', 'Android Version'),
)

class UserProfile(models.Model):
    """Profile of a unique user."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    user = models.OneToOneField(
        User, related_name='profile', on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=50, blank=True)
    roll_no = models.CharField(max_length=30, null=True, blank=True)
    ldap_id = models.CharField(max_length=50, null=True, blank=True)
    profile_pic = models.URLField(null=True, blank=True)
    fcm_id = models.CharField(max_length=200, null=True, blank=True)

    followed_bodies = models.ManyToManyField('bodies.Body', related_name='followers', blank=True)
    contact_no = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    about = models.TextField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    department = models.CharField(max_length=30, null=True, blank=True)
    department_name = models.CharField(max_length=200, null=True, blank=True)
    degree = models.CharField(max_length=200, null=True, blank=True)
    degree_name = models.CharField(max_length=200, null=True, blank=True)
    join_year = models.IntegerField(null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)

    roles = models.ManyToManyField('roles.BodyRole', related_name='users', blank=True)
    former_roles = models.ManyToManyField('roles.BodyRole', related_name='former_users', blank=True)
    institute_roles = models.ManyToManyField(
        'roles.InstituteRole', related_name='users', blank=True)
    hostel = models.CharField(max_length=100, null=True, blank=True)
    room = models.CharField(max_length=30, null=True, blank=True)

    android_version = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return self.name

class WebPushSubscription(models.Model):
    """One web push subscription."""
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='web_push_subscriptions')
    endpoint = models.TextField()
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=100)

    def __str__(self):
        return self.user.name

class UserTagCategory(models.Model):
    """A category of tags.
    A user will typically have only only one tag from each category."""
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class UserTag(models.Model):
    """A single tag that a user can match."""

    category = models.ForeignKey(UserTagCategory, on_delete=models.CASCADE)
    target = models.CharField(max_length=40, choices=TAG_TARGET_CHOICES)
    regex = models.CharField(max_length=150)
    secondary_target = models.CharField(max_length=40, choices=TAG_TARGET_CHOICES, blank=True, null=True)
    secondary_regex = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return '%s %s' % (self.target, self.regex)

    def match(self, user):
        """Match a user with a tag and return a Match object."""
        matched = self.match_regex(user, self.target, self.regex)
        return matched if matched else self.match_secondary(user)

    def match_secondary(self, user):
        """Match a user with the secondary target and return a Match object."""
        return self.match_regex(user, self.secondary_target, self.secondary_regex)

    @staticmethod
    def match_regex(user, target, regex):
        """Match the user with particular regex."""
        if target and regex and getattr(user, target):
            return re.match(regex, getattr(user, target))
        return None
