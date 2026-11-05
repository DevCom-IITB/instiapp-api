from django.conf import settings
from rest_framework.response import Response
from rest_framework import viewsets
from placements.models import BlogEntry
from placements.serializers import BlogEntrySerializer
from roles.helpers import login_required_ajax
from helpers.misc import query_from_num
from helpers.misc import query_search
from alumni.models import AlumniUser
from users.models import UserProfile
from placements.cache import get_top_100_blogs


class PlacementBlogViewset(viewsets.ViewSet):
    @classmethod
    @login_required_ajax
    def placement_blog(cls, request):
        """Get Placement Blog."""
        # Retrieve the UserProfile of the logged-in user
        user_profile = UserProfile.objects.get(user=request.user)

        # Check if the ldap of the UserProfile exists in the AlumniUser model
        if AlumniUser.objects.filter(ldap=user_profile.ldap_id).exists():
            return Response({"error": "Alumni cannot access this page."}, status=403)

        search_query = request.GET.get("query", "").strip()
        from_q = request.GET.get("from")
        num_q = request.GET.get("num")
        from_i = int(from_q) if from_q is not None and str.isdigit(from_q) else 0
        num = int(num_q) if num_q is not None and str.isdigit(num_q) else 20

        # FAST PATH: Serve slice from Redis (Top 100, no search query)
        if not search_query and (from_i + num <= 100):
            cached_posts = get_top_100_blogs("placement", settings.PLACEMENTS_URL_VAL)
            return Response(cached_posts[from_i : from_i + num])

        # SLOW PATH: Search query or deep pagination -> query database
        queryset = BlogEntry.objects.filter(blog_url=settings.PLACEMENTS_URL_VAL)
        queryset = query_search(request, 3, queryset, ["title", "content"], "placement")
        # queryset = queryset.order_by('-pinned', "-published")
        queryset = query_from_num(request, 20, queryset)

        return Response(BlogEntrySerializer(queryset, many=True).data)

    @classmethod
    @login_required_ajax
    def training_blog(cls, request):
        """Get Training Blog."""
        search_query = request.GET.get("query", "").strip()
        from_q = request.GET.get("from")
        num_q = request.GET.get("num")
        from_i = int(from_q) if from_q is not None and str.isdigit(from_q) else 0
        num = int(num_q) if num_q is not None and str.isdigit(num_q) else 20

        # FAST PATH: Serve slice from Redis (Top 100, no search query)
        if not search_query and (from_i + num <= 100):
            cached_posts = get_top_100_blogs("training", settings.TRAINING_BLOG_URL_VAL)
            return Response(cached_posts[from_i : from_i + num])

        # SLOW PATH: Search query or deep pagination -> query database
        queryset = BlogEntry.objects.filter(blog_url=settings.TRAINING_BLOG_URL_VAL)
        queryset = query_search(request, 3, queryset, ["title", "content"], "training")
        # queryset = queryset.order_by('-pinned', "-published")
        queryset = query_from_num(request, 20, queryset)
        return Response(BlogEntrySerializer(queryset, many=True).data)
