"""Model for UserProfile."""
from __future__ import unicode_literals
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """Profile of a unique user."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    user = models.OneToOneField(
        User, related_name='profile', on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=50, blank=True)
    roll_no = models.CharField(max_length=10, null=True, blank=True)
    ldap_id = models.CharField(max_length=50, null=True, blank=True)
    profile_pic = models.URLField(null=True, blank=True)
    fcm_id = models.CharField(max_length=200, null=True, blank=True)

    followed_bodies = models.ManyToManyField('bodies.Body', related_name='followers', blank=True)
    contact_no = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    about = models.TextField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    department = models.CharField(max_length=10, null=True, blank=True)
    department_name = models.CharField(max_length=200, null=True, blank=True)
    degree = models.CharField(max_length=200, null=True, blank=True)
    degree_name = models.CharField(max_length=200, null=True, blank=True)
    join_year = models.IntegerField(null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)

    roles = models.ManyToManyField('roles.BodyRole', related_name='users', blank=True)
    institute_roles = models.ManyToManyField(
        'roles.InstituteRole', related_name='users', blank=True)
    hostel = models.TextField(blank=True, null=True)
    room = models.TextField(default=1, null=True, blank=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return self.name

    # @receiver(post_save, sender=User)
    # def create_user_profile(sender, instance, created, **kwargs):
    #     if created:
    #         p = Profile.objects.create(user=instance)

    # @receiver(post_save, sender=User)
    # def save_user_profile(sender, instance, **kwargs):
    #     instance.profile.save()
