from django.contrib import admin

from buyandsell.models import Ban, Category, ImageURL, Product, Report

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ImageURL)
admin.site.register(Report)
admin.site.register(Ban)
