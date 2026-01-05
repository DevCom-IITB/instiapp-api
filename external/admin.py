from django.contrib import admin
from external.models import ExternalBlogEntry


class ExternalBlogAdmin(admin.ModelAdmin):
    list_filter = ("published",)
    list_display = ("title", "body", "published")
    search_fields = ["title"]


admin.site.register(ExternalBlogEntry, ExternalBlogAdmin)
