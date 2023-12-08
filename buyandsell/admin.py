from django.contrib import admin

from buyandsell.models import Ban, Category, ImageURL, Product, Report

# Register your models here.
admin.site.register(Category)
admin.site.register(ImageURL)
admin.site.register(Report)
admin.site.register(Ban)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "description",
        "brand",
        "time_of_creation",
        "deleted",
        "status",
    )
    list_filter = ("status", "deleted")
    search_fields = ("title", "category", "user")
    ordering = ("-time_of_creation",)


admin.site.register(Product, ProductAdmin)
