from django.contrib import admin
from querybot.models import Query, UnresolvedQuery

admin.site.register(Query)
admin.site.register(UnresolvedQuery)