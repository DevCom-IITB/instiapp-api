from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.crypto import get_random_string
from django.dispatch import receiver
import uuid

class Users(models.Model):


    user = models.OneToOneField(User, on_delete=models.CASCADE,blank=True,null=True)

    unique_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=50)
    roll_no = models.CharField(max_length=10, null =True)
    profile_pic = models.URLField(null = True)
    gcm_id = models.IntegerField(  null = True)
    # mode_of_login = models.CharField(max_length=1, choices=LOGIN_CHOICES, default='C')
    # college = models.CharField(max_length=200)
    # contact_no = models.CharField(max_length=10, null= True)
    email = models.EmailField()
    year = models.IntegerField(default=1 , null =True)
    # programme_of_study = models.CharField(max_length=20, choices=PROGRAM_CHOICES, null=True)
    about = models.TextField(blank=True, null = True)
    # interests = models.ManyToManyField(Tag)
    # ldap_uid = models.IntegerField(null=True, blank=True)
    # first_time_login = models.BooleanField(default=True)
    # unique_token = models.CharField(max_length=32, default=random_32_length_string, editable=False)

    # class Meta:
    #     verbose_name = "Profile"
    #     verbose_name_plural = "Profiles"

    def __str__(self):
        return self.name

    # @receiver(post_save, sender=User)
    # def create_user_profile(sender, instance, created, **kwargs):
    #     if created:
    #         p = Profile.objects.create(user=instance)

    # @receiver(post_save, sender=User)
    # def save_user_profile(sender, instance, **kwargs):
    #     instance.profile.save()