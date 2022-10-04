from django.contrib import admin
from community.models import Community, CommunityPost, CommunityPostUserReaction

admin.site.register(Community)
admin.site.register(CommunityPost)
admin.site.register(CommunityPostUserReaction)
