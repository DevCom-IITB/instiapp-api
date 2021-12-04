from django.contrib import admin

from buyandsell.models import Category, ImageURL, Product

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ImageURL)