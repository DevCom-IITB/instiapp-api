from uuid import uuid4

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from helpers.misc import get_url_friendly

PDT_NAME_MAX_LENGTH = 60
CONTACT_MAX_LENGTH = 300


def get_image_path(instance, filename):
    # NOTE: Since we not using uploaded by - all the images are stored in the same folder.
    random_str = "fd9a457a-a5b5-4560-b81e-6654129e5df8"
    return './' + random_str[0:4] + '/' + random_str + '-' + filename + '.jpg'

class ProductFound(models.Model):
    CATEGORY_CHOICES = (
        ("electronics", "Electronics"),
        ("stationery", "Stationery"),
        ("Other", "Other"),
    )

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    str_id = models.CharField(max_length=58, editable=False, null=True)
    name = models.CharField(max_length=PDT_NAME_MAX_LENGTH, blank=False, null=False)
    description = models.TextField(blank=True, default="", null=False)
    product_image = models.TextField(
        blank=True, null=True
    )  # Contains URLs of all three images.
    product_image1 = models.ImageField(
        upload_to=get_image_path, null=False, blank=False
    )
    product_image2 = models.ImageField(upload_to=get_image_path, null=False, blank=True)
    product_image3 = models.ImageField(upload_to=get_image_path, null=False, blank=True)
    category = models.CharField(
        choices=CATEGORY_CHOICES, null=True, blank=True, max_length=PDT_NAME_MAX_LENGTH
    )
    found_at = models.CharField(
        max_length=PDT_NAME_MAX_LENGTH, blank=True, null=False, default=""
    )

    claimed = models.BooleanField(default=False, blank=True, null=True)
    contact_details = models.CharField(
        max_length=CONTACT_MAX_LENGTH, blank=False, null=False
    )
    time_of_creation = models.DateTimeField(auto_now_add=True)

    claimed_by = models.ForeignKey(
        "users.UserProfile",
        on_delete=models.CASCADE,
        related_name="claimed_products",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # NOTE: The ProductFound object is updated after the images are saved.
        if self.claimed_by is not None:
            self.claimed = True
        else:
            self.claimed = False
        self.str_id = get_url_friendly(self.name) + "-" + str(self.id)[:8]
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "ProductFound"
        verbose_name_plural = "ProductsFound"
        ordering = ("-time_of_creation",)
        indexes = [
            models.Index(
                fields=[
                    "time_of_creation",
                ]
            ),
        ]


@receiver(post_save, sender=ProductFound, dispatch_uid="update_product_found")
def update_product_found(sender, instance, **kwargs):
    """Update the product_image field of ProductFound after the image is saved.
    This is done to avoid the problem of the correct image url not being available."""
    image_urls = ""
    image_urls += instance.product_image1.url + ","
    if instance.product_image2:
        image_urls += instance.product_image2.url + ","
    if instance.product_image3:
        image_urls += instance.product_image3.url

    sender.objects.filter(id=instance.id).update(product_image=image_urls)
