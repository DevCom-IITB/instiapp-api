from django.contrib import admin
from .models import PlacementCompanyThread, PlacementBlogPost, PlacementExtractedData

class PlacementCompanyThreadAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_slug', 'domain', 'first_post_date')
    search_fields = ('company_name', 'domain')

class PlacementBlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'published')
    search_fields = ('title', 'content')
    list_filter = ('published',)

class PlacementExtractedDataAdmin(admin.ModelAdmin):
    list_display = ('post', 'deadline', 'role', 'domain')
    search_fields = ('role', 'domain', 'venue')

admin.site.register(PlacementCompanyThread, PlacementCompanyThreadAdmin)
admin.site.register(PlacementBlogPost, PlacementBlogPostAdmin)
admin.site.register(PlacementExtractedData, PlacementExtractedDataAdmin)
