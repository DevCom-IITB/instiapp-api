from django.contrib import admin
from .models import CompanyThread, BlogPost, ExtractedData

class CompanyThreadAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_slug', 'domain', 'first_post_date')
    search_fields = ('company_name', 'domain')

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('raw_company_name', 'thread', 'published')
    search_fields = ('raw_company_name', 'raw_content')
    list_filter = ('published',)

class ExtractedDataAdmin(admin.ModelAdmin):
    list_display = ('post', 'deadline', 'role', 'domain')
    search_fields = ('role', 'domain', 'venue')

admin.site.register(CompanyThread, CompanyThreadAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(ExtractedData, ExtractedDataAdmin)
