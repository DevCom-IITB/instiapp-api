"""Model for UserProfile."""
from __future__ import unicode_literals
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
#from django.db.models.signals import post_save
#from django.utils.crypto import get_random_string
#from django.dispatch import receiver

class UserProfile(models.Model):
    """Profile of a unique user."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    name = models.CharField(max_length=50, blank=True)
    roll_no = models.CharField(max_length=10, null=True, blank=True)
    profile_pic = models.URLField(null=True, blank=True)
    fcm_id = models.IntegerField(null=True, blank=True)

    followed_bodies = models.ManyToManyField('bodies.Body', related_name='followers', blank=True)
    # mode_of_login = models.CharField(max_length=1, choices=LOGIN_CHOICES, default='C')
    contact_no = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    year = models.IntegerField(default=1, null=True, blank=True)
    # programme_of_study = models.CharField(max_length=20, choices=PROGRAM_CHOICES, null=True)
    about = models.TextField(blank=True, null=True)
    # interests = models.ManyToManyField(Tag)
    # ldap_uid = models.IntegerField(null=True, blank=True)
    # first_time_login = models.BooleanField(default=True)
    # unique_token = models.CharField(
    #     max_length=32, default=random_32_length_string, editable=False)

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE, null=True, blank=True)

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
