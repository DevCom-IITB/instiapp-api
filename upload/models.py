"""Models for Uploaded Images."""
from uuid import uuid4
from django.db import models

class UploadedImage(models.Model):
    """An uploaded file."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('users.UserProfile', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='uploaded_images')
    picture = models.ImageField(upload_to='.')

    class Meta:
        verbose_name = "Uploaded Image"
        verbose_name_plural = "Uploaded Images"
