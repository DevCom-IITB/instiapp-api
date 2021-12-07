from notifications.signals import notify

from django.contrib import admin
from django.contrib.auth.models import User
from querybot.models import Query, UnresolvedQuery

def handle_entry(entry, notify_user=True):
    """Handle a single entry from a feed."""

    # Try to get an entry existing
    db_entry = UnresolvedQuery.objects.filter(id=entry.id).first()

    # Send notifications to user
    users = User.objects.filter(id=db_entry.user.user.id)
    if notify_user:
        notify.send(db_entry, recipient=users, verb="Your query has been resolved check the updated list of questions")

    db_entry.delete()

class QueryAdmin(admin.ModelAdmin):
    search_fields = ['question', 'category']
    list_display = ('question', 'category')
    list_filter = ['category']


admin.site.register(Query, QueryAdmin)

@admin.action(description='Mark selected queries as resolved')
def make_resolved(modeladmin, request, queryset):
    for entry in queryset:
        handle_entry(entry)

class UnresolvedQueryAdmin(admin.ModelAdmin):
    search_fields = ['question', 'category']
    list_display = ('user', 'question', 'category')
    list_filter = ['category']
    actions = [make_resolved]


admin.site.register(UnresolvedQuery, UnresolvedQueryAdmin)
