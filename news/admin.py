from django.contrib import admin
from news.models import NewsEntry

class NewsAdmin(admin.ModelAdmin):
    list_filter = ('published',)
    list_display = ('title', 'body', 'published')
    ordering = ('-published',)


admin.site.register(NewsEntry, NewsAdmin)
