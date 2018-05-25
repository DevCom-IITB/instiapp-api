from django.contrib import admin
from news.models import NewsEntry, NewsSource

admin.site.register(NewsEntry)
admin.site.register(NewsSource)
