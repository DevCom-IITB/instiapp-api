"""Models for Uploaded Images."""
from uuid import uuid4
from django.db import models
from PIL import Image

def get_image_path(instance, filename):
    userid = str(instance.uploaded_by.id)
    return './' + userid[0:2] + '/' + userid[2:4] + '/' + userid + '-' + filename

class UploadedImage(models.Model):
    """An uploaded file."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('users.UserProfile', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='uploaded_images')
    picture = models.ImageField(upload_to=get_image_path)

    class Meta:
        verbose_name = "Uploaded Image"
        verbose_name_plural = "Uploaded Images"
        ordering = ("-time_of_creation",)

    def save(self, *args, **kwargs):
        # Super
        saved = super(UploadedImage, self).save(*args, **kwargs)

        # Resize Image
        if self.pk and self.picture:
            self.resize(self.picture.path)

        return saved

    def __str__(self):
        return str(self.time_of_creation)

    @staticmethod
    def resize(path):
        """Resize image."""
        # Maximum Dimension
        MAX_DIM = 800

        # Load image
        image = Image.open(path)
        (width, height) = image.size

        # Resize
        factor = min(MAX_DIM / height, MAX_DIM / width)
        if factor < 0.85:
            size = (int(width * factor), int(height * factor))
            image = image.resize(size, Image.ANTIALIAS)

            # Save
            image.save(path)
