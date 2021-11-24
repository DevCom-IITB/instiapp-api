from django.contrib import admin
from querybot.models import Query, UnresolvedQuery

class QueryAdmin(admin.ModelAdmin):
    search_fields = ['question', 'category']
    list_display = ('question', 'category')
    list_filter = ['category']


admin.site.register(Query, QueryAdmin)

@admin.action(description='Mark selected queries as resolved')
def make_resolved(modeladmin, request, queryset):
    queryset.update(resolved=True)

class UnresolvedQueryAdmin(admin.ModelAdmin):
    search_fields = ['question', 'category']
    list_display = ('user', 'question', 'category')
    list_filter = ['category']
    actions = [make_resolved]


admin.site.register(UnresolvedQuery, UnresolvedQueryAdmin)
