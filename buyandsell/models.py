from uuid import uuid4
from django.db.models.deletion import SET
from django.db.models.fields.related import ForeignKey
from django.db import models
from helpers.misc import get_url_friendly

PDT_NAME_MAX_LENGTH = 60
CONTACT_MAX_LENGTH = 300
MOD_EMAIL = "hardikraj08@gmail.com"


# Create your models here.
class Category(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    numproducts = models.IntegerField(default=0, null=False, blank=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    # achievements, events, users
    # placement
    CATEGORY_CHOICES = (
        ("electronics", "Electronics"),
        ("stationery", "Stationery"),
        ("Other", "Other"),
    )
    CONDITION_CHOICES = (
        ("1", "01/10"),
        ("2", "02/10"),
        ("3", "03/10"),
        ("4", "04/10"),
        ("5", "05/10"),
        ("6", "06/10"),
        ("7", "07/10"),
        ("8", "08/10"),
        ("9", "09/10"),
        ("10", "10/10"),
    )
    ACTION_CHOICES = (
        ("sell", "Sell"),
        ("giveaway", "Give Away"),
        ("rent", "Rent"),
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    str_id = models.CharField(max_length=58, editable=False, null=True)
    name = models.CharField(max_length=PDT_NAME_MAX_LENGTH, blank=False, null=False)
    description = models.TextField(blank=True, default="", null=False)
    product_image = models.TextField(blank=True, null=True)
    # TODO: Change the on_delete function to .
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    brand = models.CharField(
        max_length=PDT_NAME_MAX_LENGTH, blank=True, null=False, default=""
    )
    warranty = models.BooleanField(default=False)
    packaging = models.BooleanField(default=False)
    condition = models.CharField(
        max_length=2, choices=CONDITION_CHOICES, default="7", blank=False
    )
    followers = models.ManyToManyField(
        "users.UserProfile", related_name="productsfollowed", blank=True
    )
    action = models.CharField(
        max_length=10, choices=ACTION_CHOICES, default="sell", blank=False
    )
    status = models.BooleanField(default=True, blank=True, null=True)
    deleted = models.BooleanField(default=False, blank=True, null=True)
    price = models.IntegerField(blank=False, default=100)
    negotiable = models.BooleanField(default=True)
    user = models.ForeignKey(
        "users.UserProfile", on_delete=models.CASCADE, related_name="products"
    )
    contact_details = models.CharField(
        max_length=CONTACT_MAX_LENGTH, blank=False, null=False
    )
    time_of_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # self.category.numproducts+=1
        self.str_id = get_url_friendly(self.name) + "-" + str(self.id)[:8]
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        #  self.category.numproducts-=1
        return super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ("-time_of_creation",)
        indexes = [
            models.Index(
                fields=[
                    "time_of_creation",
                ]
            ),
        ]
        # order by count of followers


class ImageURL(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    url = models.URLField(blank=False, null=False)

    def __str__(self):
        return self.url


class Ban(models.Model):
    user = models.ManyToManyField("users.UserProfile")
    endtime = models.DateTimeField()

    def __str__(self):
        return str(self.user)


class Limit(models.Model):
    user = models.ForeignKey("users.UserProfile", on_delete=models.CASCADE)
    endtime = models.DateTimeField(auto_created=True, null=True)
    strikes = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user)


class Report(models.Model):
    moderator_email = MOD_EMAIL
    product = ForeignKey(Product, on_delete=models.CASCADE)
    reporter = ForeignKey("users.UserProfile", on_delete=SET("User_DNE"))
    reason = models.TextField(blank=False, null=False)
    addressed = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.product) + ":" + str(self.reporter)
