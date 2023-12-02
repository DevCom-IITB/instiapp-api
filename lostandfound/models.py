from django.db.models import deletion
from django.db.models.deletion import SET
from django.db.models.fields.related import ForeignKey
from django.utils import timezone
from django.db import models
from django.db.models.enums import IntegerChoices
from uuid import uuid4
from helpers.misc import get_url_friendly
PDT_NAME_MAX_LENGTH = 60
CONTACT_MAX_LENGTH = 300

    
class ProductFound(models.Model):
    ##achievements, events, users
    # placement
    CATEGORY_CHOICES = (
        ('electronics', 'Electronics'),
        ('stationery', 'Stationery'),
        ('Other', 'Other')
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    str_id = models.CharField(max_length=58, editable=False, null=True)
    name = models.CharField(max_length=PDT_NAME_MAX_LENGTH, blank=False, null=False)
    description = models.TextField(blank=True, default='', null=False)
    product_image = models.TextField(blank=True, null=True)
    
    # TODO: Change the on_delete function to .
    category = models.CharField(choices=CATEGORY_CHOICES, null=True, blank=True, max_length=PDT_NAME_MAX_LENGTH)
    found_at = models.CharField(max_length=PDT_NAME_MAX_LENGTH, blank=True, null=False, default='')

    claimed = models.BooleanField(default=True, blank=True, null=True)

    contact_details = models.CharField(max_length=CONTACT_MAX_LENGTH, blank=False, null=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)

    claimed_by = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='claimed_products', null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
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
            models.Index(fields=['time_of_creation', ]),
        ]


