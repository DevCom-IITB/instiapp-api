"""Models for Uploaded Images."""
from uuid import uuid4
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from PIL import Image

def get_image_path(instance, filename):
    userid = str(instance.uploaded_by.id)
    return './' + userid[0:2] + '/' + userid[2:4] + '/' + userid + '-' + filename + '.jpg'

class UploadedImage(models.Model):
    """An uploaded file."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('users.UserProfile', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='uploaded_images')
    picture = models.ImageField(upload_to=get_image_path)

    claimant_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    claimant_id = models.UUIDField(null=True)
    claimant = GenericForeignKey('claimant_type', 'claimant_id')
    is_claimed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Uploaded Image"
        verbose_name_plural = "Uploaded Images"
        ordering = ("-time_of_creation",)
        indexes = [
            models.Index(fields=['is_claimed', ]),
        ]

    def save(self, *args, **kwargs):
        # Super
        super(UploadedImage, self).save(*args, **kwargs)

        # Resize Image
        if self.pk and self.picture:
            self.resize_convert(self.picture.path)

    def __str__(self):
        return str(self.time_of_creation)

    @staticmethod
    def resize_convert(path):
        """Resize image and convert to JPG."""
        # Maximum Dimension
        MAX_DIM = 1200

        # Load image
        image = Image.open(path).convert('RGB')
        (width, height) = image.size

        # Resize
        factor = min(MAX_DIM / height, MAX_DIM / width)
        if factor < 0.85:
            size = (int(width * factor), int(height * factor))
            image = image.resize(size, Image.ANTIALIAS)

        # Save
        image.save(path, 'JPEG', quality=90, optimize=True, progressive=True)

@receiver(post_delete, sender=UploadedImage)
def image_post_delete_handler(**kwargs):
    image = kwargs['instance']
    storage, path = image.picture.storage, image.picture.path
    storage.delete(path)
