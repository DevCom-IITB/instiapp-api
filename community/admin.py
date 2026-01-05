from django.contrib import admin
from community.models import Community, CommunityPost, CommunityPostUserReaction, Poll, PollOption, PollVote



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

class PollOptionInline(admin.TabularInline):
    """Manage poll options inside poll admin"""
    model = PollOption
    extra = 3  # Show 3 empty option fields by default
    fields = ['text', 'order', 'vote_count']
    readonly_fields = ['vote_count']
    ordering = ['order']


class PollVoteInline(admin.TabularInline):
    """Manage poll votes inside poll admin"""
    model = PollVote
    extra = 0
    fields = ['user', 'option', 'voted_at']
    readonly_fields = ['voted_at']
    raw_id_fields = ['user']
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('user', 'option')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filter the 'option' dropdown to only show options for the current poll.
        """
        # Check if we are modifying the 'option' field's form
        if db_field.name == "option":
            # Get the ID of the parent Poll object from the URL
            poll_id = request.resolver_match.kwargs.get('object_id')
            if poll_id:
                # Set the queryset for the dropdown to options of this poll only
                kwargs["queryset"] = PollOption.objects.filter(poll_id=poll_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ✅ Main Poll admin with inlines
@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'community_post_preview', 'allow_multiple_answers', 'created_at', 'total_votes', 'total_options']
    search_fields = ['question', 'community_post__content']
    list_filter = ['allow_multiple_answers', 'created_at']
    readonly_fields = ['created_at', 'total_votes', 'total_options']
    raw_id_fields = ['community_post']
    
    # ✅ Include both inlines
    inlines = [PollOptionInline, PollVoteInline]
    
    # Custom display methods
    def question_preview(self, obj):
        """Show truncated question"""
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question'
    
    def community_post_preview(self, obj):
        """Show truncated post content"""
        content = obj.community_post.content or "No content"
        return content[:30] + "..." if len(content) > 30 else content
    community_post_preview.short_description = 'Post'
    
    def total_votes(self, obj):
        """Display total votes for this poll"""
        return PollVote.objects.filter(poll=obj).count()
    total_votes.short_description = 'Total Votes'
    
    def total_options(self, obj):
        """Display total options for this poll"""
        return obj.options.count()
    total_options.short_description = 'Options'
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('community_post').prefetch_related('options', 'votes')


admin.site.register(Community)
admin.site.register(CommunityPost, CommunityPostAdmin)
admin.site.register(CommunityPostUserReaction)
