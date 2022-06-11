from uuid import uuid4
from django.db import models
from helpers.misc import get_url_friendly
class idf_Post(models.Model):
    id=models.UUIDField(primary_key=True, editable=False, default=uuid4)
    content=models.TextField(blank=True) #this will store the content of the post
    image_url = models.URLField(blank=True, null=True) #for the image of the post
    notification=models.BooleanField(default=True) #whenever a new post is created the notification field will will be initialized with the default value true thus sending the user a notification
    posted_by=models.ForeignKey('users.UserProfile', null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='posted')#to store info of the user posting
    website_url= models.URLField(blank=True, null=True)#to save any links by the user in the post
    #reactions need emojis
 
    