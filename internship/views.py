from rest_framework import generics
from .models import CompanyThread, BlogPost
from .serializers import CompanyThreadSerializer, CompleteThreadSerializer, BlogPostSerializer
from django.db.models import OuterRef, Subquery

class ThreadListView(generics.ListAPIView):

    queryset = CompanyThread.objects.all().order_by('-first_post_date')
    serializer_class = CompanyThreadSerializer
    
    # Can do pagination too

class ThreadDetailView(generics.RetrieveAPIView):

    queryset = CompanyThread.objects.prefetch_related('posts__extracted')
    serializer_class = CompleteThreadSerializer
    
    lookup_field = 'company_slug'

class BlogPostListView(generics.ListAPIView):

    queryset = BlogPost.objects.select_related('extracted').order_by('-published')
    serializer_class = BlogPostSerializer

class LatestCompanyPostListView(generics.ListAPIView):
    serializer_class = BlogPostSerializer

    def get_queryset(self):

        latest_post_subquery = BlogPost.objects.filter(
            thread=OuterRef('thread')
        ).order_by('-published').values('id')[:1]

        #Filter the main BlogPost table to only include those exact IDs, 
        return BlogPost.objects.filter(
            id=Subquery(latest_post_subquery)
        ).select_related('extracted').order_by('-published')