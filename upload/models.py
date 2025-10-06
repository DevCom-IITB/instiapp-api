"""Models for Uploaded Images."""
from uuid import uuid4
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from PIL import Image
import os


def get_image_path(instance, filename):
    userid = str(instance.uploaded_by.id)
    return (
        "./" + userid[0:2] + "/" + userid[2:4] + "/" + userid + "-" + filename + ".jpg"
    )

def get_file_path(instance, filename):
    userid = str(instance.uploaded_by.id)
    name, ext = os.path.splitext(filename)
    return f"./{userid[0:2]}/{userid[2:4]}/{userid}-{name}{ext}"


class UploadedFile(models.Model):
    """An uploaded file."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        "users.UserProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_files",
    )
    file = models.FileField(upload_to=get_file_path)
    # original_filename = models.CharField(max_length=255, blank=True)
    # file_size = models.PositiveIntegerField(null=True, blank=True)  # Size in bytes
    # content_type = models.CharField(max_length=100, blank=True)
    # FILE_TYPE_CHOICES = [
    #     ('image', 'Image'),
    #     ('document', 'Document'),
    #     ('video', 'Video'),
    #     ('audio', 'Audio'),
    #     ('other', 'Other'),
    # ]
    # file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='other')


    claimant_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    claimant_id = models.UUIDField(null=True)
    claimant = GenericForeignKey("claimant_type", "claimant_id")
    is_claimed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Uploaded File"
        verbose_name_plural = "Uploaded Files"
        ordering = ("-time_of_creation",)
        indexes = [
            models.Index(
                fields=[
                    "is_claimed",
                ]
            ),
        ]

    def save(self, *args, **kwargs):  # pylint: disable=W0222
        # if self.file:
            # self.original_filename = self.file.name
            # self.file_size = self.file.size
            # self.content_type = getattr(self.file.file, 'content_type', '')
            # self.file_type = self._determine_file_type()
        # Super
        super().save(*args, **kwargs)

        # Resize Image
        # if self.pk and self.file and self.file_type == 'image':
        #     try:
        #         self.resize_convert(self.file.path)
        #     except Exception as e:
        #         print(f"Failed to resize image: {e}")
        # Try to resize if file is an image (by extension)
        if self.pk and self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            if ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]:
                try:
                    self.resize_convert(self.file.path)
                except Exception as e:
                    print(f"Failed to resize image: {e}")

    def __str__(self):
        return str(self.time_of_creation)
    
    # def _determine_file_type(self):
    #     """Determine file type based on content type or extension."""
    #     if not self.content_type:
    #         return 'other'
            
    #     if self.content_type.startswith('image/'):
    #         return 'image'
    #     elif self.content_type.startswith('video/'):
    #         return 'video'
    #     elif self.content_type.startswith('audio/'):
    #         return 'audio'
    #     elif self.content_type in ['application/pdf', 'application/msword', 
    #                                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    #                                'text/plain', 'application/rtf']:
    #         return 'document'
    #     else:
    #         return 'other'
        
    def __str__(self):
        return f"({self.time_of_creation})"
    
    # @property
    # def file_url(self):
    #     """Get file URL."""
    #     if self.file:
    #         return self.file.url
    #     return None

    # @property
    # def is_image(self):
    #     """Check if file is an image."""
    #     return self.file_type == 'image'

    @staticmethod
    def resize_convert(path):
        """Resize image and convert to JPG."""
        # Maximum Dimension
        try:
            MAX_DIM = 1200

            # Load image
            image = Image.open(path).convert("RGB")
            (width, height) = image.size

            # Resize
            factor = min(MAX_DIM / height, MAX_DIM / width)
            if factor < 0.85:
                size = (int(width * factor), int(height * factor))
                image = image.resize(size, Image.LANCZOS)

            base_path = os.path.splitext(path)[0]
            jpeg_path = f"{base_path}.jpg"
            image.save(jpeg_path, "JPEG", quality=90, optimize=True, progressive=True)
                
                # Remove original if different format
            if path != jpeg_path:
                os.remove(path)
        except Exception as e:
            print(f"Error processing image {path}: {e}")

UploadedImage = UploadedFile


@receiver(post_delete, sender=UploadedFile)
def file_post_delete_handler(**kwargs):
    file_obj = kwargs["instance"]
    if file_obj.file:
        storage, path = file_obj.file.storage, file_obj.file.path
        if storage.exists(path):
            storage.delete(path)
