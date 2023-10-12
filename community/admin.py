from django.contrib import admin
from community.models import Community, CommunityPost, CommunityPostUserReaction


class CommunityPostAdmin(admin.ModelAdmin):
    search_fields = ["content", "community__name", "posted_by__name"]
    list_display = ("content", "community", "thread_rank", "posted_by")
    list_filter = ("community__name", "thread_rank")
    raw_id_fields = (
        "reported_by",
        "posted_by",
        "community",
        "parent",
        "reacted_by",
        "followed_by",
        "interests",
        "tag_user",
        "tag_body",
        "tag_location",
    )


admin.site.register(Community)
admin.site.register(CommunityPost, CommunityPostAdmin)
admin.site.register(CommunityPostUserReaction)
