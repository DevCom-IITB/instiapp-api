import csv
from django.contrib import admin
from django.contrib.auth.models import User
from django.http import HttpResponse
from notifications.signals import notify
from querybot.models import Query, UnresolvedQuery, ChatBotLog


def handle_entry(entry, notify_user=True):
    """Handle a single entry from a feed."""

    # Try to get an entry existing
    db_entry = UnresolvedQuery.objects.filter(id=entry.id).first()

    db_entry.resolved = True
    db_entry.save()

    # Send notifications to user
    users = User.objects.filter(id=db_entry.user.user.id)
    if notify_user:
        notify.send(
            db_entry,
            recipient=users,
            verb="Your query has been resolved check the updated list of questions",
        )


class QueryAdmin(admin.ModelAdmin):
    search_fields = ["question", "category"]
    list_display = ("question", "category")
    list_filter = ["category"]


admin.site.register(Query, QueryAdmin)


@admin.action(description="Mark selected queries as resolved")
def make_resolved(modeladmin, request, queryset):
    for entry in queryset:
        handle_entry(entry)


class UnresolvedQueryAdmin(admin.ModelAdmin):
    search_fields = ["question", "category"]
    list_display = ("user", "question", "category")
    list_filter = ["category", "resolved"]
    actions = [make_resolved]


def export_as_csv(self, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=a.csv"
    writer = csv.writer(response)

    writer.writerow(["question", "answer", "reaction"])
    for obj in queryset:
        writer.writerow([obj.question, obj.answer, obj.reaction])
    return response


class ChatBotLogAdmin(admin.ModelAdmin):
    search_fields = ["question", "answer"]
    list_display = ("question", "answer", "reaction")
    actions = [export_as_csv]


admin.site.register(UnresolvedQuery, UnresolvedQueryAdmin)
admin.site.register(ChatBotLog, ChatBotLogAdmin)
