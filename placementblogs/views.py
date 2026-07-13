from rest_framework import generics
from .models import PlacementCompanyThread, PlacementBlogPost
from .serializers import PlacementCompanyThreadSerializer, PlacementCompleteThreadSerializer, PlacementBlogPostSerializer
from django.db.models import OuterRef, Subquery, Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response

class InternshipPagination(PageNumberPagination):
    page_size = 20

class FilterOptionsView(APIView):
    # Returns the unique lists of domains and companies 
    def get(self, request, *args, **kwargs):
        raw_domains = PlacementCompanyThread.objects.exclude(domain__isnull=True).exclude(domain="").values_list('domain', flat=True)
        
        clean_domains = set()
        
        for raw_domain in raw_domains:
            if raw_domain:  # Just a safety check
                split_items = raw_domain.split(',') 
                for item in split_items:
                    # .strip() removes any accidental spaces before saving
                    clean_domains.add(item.strip()) 
                    
        sorted_domains = sorted(list(clean_domains))

        companies = PlacementCompanyThread.objects.values('company_name', 'company_slug').distinct().order_by('company_name')

        return Response({
            "domains": sorted_domains,
            "companies": list(companies)
        })

class PlacementThreadListView(generics.ListAPIView):
    serializer_class = PlacementCompanyThreadSerializer
    pagination_class = InternshipPagination

    def get_queryset(self):
        # Start with all threads
        queryset = PlacementCompanyThread.objects.all().order_by('-first_post_date')
        
        # Grab the filters from the URL if they exist
        domains = self.request.query_params.getlist('domain')
        companies = self.request.query_params.getlist('company')

        if domains:
            # Use Q objects to search INSIDE the comma-separated strings
            domain_query = Q()
            for d in domains:
                domain_query |= Q(domain__icontains=d.strip())
            queryset = queryset.filter(domain_query)
            
        if companies:
            # Removed the 'thread__' prefix, as we are already on the Thread model
            queryset = queryset.filter(company_slug__in=companies)
            
        return queryset
    
class PlacementThreadDetailView(generics.RetrieveAPIView):
    # Removed 'posts__extracted' and changed to just 'posts'
    queryset = PlacementCompanyThread.objects.prefetch_related('posts')
    serializer_class = PlacementCompleteThreadSerializer
    
    lookup_field = 'company_slug'

class PlacementBlogPostListView(generics.ListAPIView):
    serializer_class = PlacementBlogPostSerializer
    pagination_class = InternshipPagination

    def get_queryset(self):
        # Removed 'extracted' from select_related
        queryset = PlacementBlogPost.objects.select_related('thread').order_by('-published')
        
        domains = self.request.query_params.getlist('domain')
        companies = self.request.query_params.getlist('company')

        if domains:
            # Since we are querying Posts, we look at the connected thread's domain
            domain_query = Q()
            for d in domains:
                domain_query |= Q(thread__domain__icontains=d.strip())
            queryset = queryset.filter(domain_query)
            
        if companies:
            # Keep thread__ here because we are filtering Posts based on their Thread
            queryset = queryset.filter(thread__company_slug__in=companies)
            
        return queryset

class PlacementLatestCompanyPostListView(generics.ListAPIView):
    serializer_class = PlacementBlogPostSerializer
    pagination_class = InternshipPagination

    def get_queryset(self):
        latest_post_subquery = PlacementBlogPost.objects.filter(
            thread=OuterRef('thread')
        ).order_by('-published').values('id')[:1]

        # Filter the main PlacementBlogPost table to only include those exact IDs
        # Removed 'extracted' from select_related
        return PlacementBlogPost.objects.filter(
            id=Subquery(latest_post_subquery)
        ).select_related('thread').order_by('-published')