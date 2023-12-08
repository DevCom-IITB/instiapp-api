from django.contrib import admin
from placements.models import BlogEntry


class BlogEntryAdmin(admin.ModelAdmin):
    list_filter = ("published",)
    list_display = ("title", "published")
    search_fields = ["title"]


admin.site.register(BlogEntry, BlogEntryAdmin)
