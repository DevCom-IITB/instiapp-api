from __future__ import unicode_literals
from django.db import models

class User(models.Model):

    mapped_user = models.OneToOneField("self", on_delete=models.CASCADE,blank=True,null=True)
   
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    # mode_of_login = models.CharField(max_length=1, choices=LOGIN_CHOICES, default='C')
    # college = models.CharField(max_length=200)
    contact_no = models.CharField(max_length=10)
    email = models.EmailField()
    year = models.IntegerField(default=1)
    # programme_of_study = models.CharField(max_length=20, choices=PROGRAM_CHOICES, null=True)
    # about = models.TextField(blank=True)
    # interests = models.ManyToManyField(Tag)
    # ldap_id = models.IntegerField(null=True, blank=True)
    # first_time_login = models.BooleanField(default=True)
    # unique_token = models.CharField(max_length=32, default=random_32_length_string, editable=False)

    # class Meta:
    #     verbose_name = "Profile"
    #     verbose_name_plural = "Profiles"

    # def __str__(self):
    #     return self.name

    # @receiver(post_save, sender=User)
    # def create_user_profile(sender, instance, created, **kwargs):
    #     if created:
    #         p = Profile.objects.create(user=instance)

    # @receiver(post_save, sender=User)
    # def save_user_profile(sender, instance, **kwargs):
    #     instance.profile.save()