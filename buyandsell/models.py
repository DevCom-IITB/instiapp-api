from django.utils import timezone
from django.db import models
from django.db.models.enums import IntegerChoices
from uuid import uuid4
PDT_NAME_MAX_LENGTH = 60
CONTACT_MAX_LENGTH = 300
# Create your models here.
class Product(models.Model):
    ###Display followers to buyers, sellers.
    ###Add product tags.
    ###multiselect for action?
    ##achievements, events, users 
    # placement
    CONDITION_CHOICES = (
        ('1','01/10'),
        ('2','02/10'),
        ('3','03/10'),
        ('4','04/10'),
        ('5','05/10'),
        ('6','06/10'),
        ('7','07/10'),
        ('8','08/10'),
        ('9','09/10'),
        ('10','10/10'),
    )
    ACTION_CHOICES = (
        ('sell', 'Sell'),
        ('giveaway', 'Give Away'),
        ('rent', 'Rent'),
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=PDT_NAME_MAX_LENGTH, blank=False, null=False)
    description = models.TextField(blank=True, default='', null=False)
    brand = models.CharField(max_length=PDT_NAME_MAX_LENGTH, blank=True,null=False,default='')
    warranty = models.BooleanField(default=False)
    packaging = models.BooleanField(default=False)
    condition = models.CharField(max_length=2,choices=CONDITION_CHOICES, default='7',blank=False)
    
    
    followers = models.ManyToManyField('users.UserProfile', related_name='followers+', blank=True)


    action = models.CharField(max_length=10,choices=ACTION_CHOICES, default='sell', blank=False)
    status = models.BooleanField(default=True)
    price = models.IntegerField(blank=False, default=100)
    negotiable = models.BooleanField(default=True)
    
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE)
    contact_details = models.CharField(max_length=CONTACT_MAX_LENGTH, blank=False, null=False)
    time_of_creation  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ("-time_of_creation",)
        indexes = [
            models.Index(fields=['time_of_creation', ]),
        ]
        #order by count of followers
class ImageURL(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    url = models.URLField(blank=False, null=False)
class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=60, blank=False, null=False)
    numproducts = models.IntegerField(default=0, null=False, blank=False)