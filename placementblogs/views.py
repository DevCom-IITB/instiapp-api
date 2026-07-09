from rest_framework import generics
from .models import PlacementCompanyThread, PlacementBlogPost
from .serializers import PlacementCompanyThreadSerializer, PlacementCompleteThreadSerializer, PlacementBlogPostSerializer
from django.db.models import OuterRef, Subquery
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
class InternshipPagination(PageNumberPagination):
    page_size = 20

class FilterOptionsView(APIView):
    #Returns the unique lists of domains, categories, and companies 
    def get(self, request, *args, **kwargs):
        # .exclude() drops empty values, .distinct() removes duplicates
        domains = PlacementCompanyThread.objects.exclude(domain__isnull=True).exclude(domain="").values_list('domain', flat=True).distinct().order_by('domain')
        companies = PlacementCompanyThread.objects.values('company_name', 'company_slug').distinct().order_by('company_name')

        # Return a simple dictionary for the frontend
        return Response({
            "domains": list(domains),
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

        # If the list is not empty, filter using __in
        if domains:
            queryset = queryset.filter(extracted__domain__in=domains)
        if companies:
            queryset = queryset.filter(thread__company_slug__in=companies)
            
        return queryset
    
class PlacementThreadDetailView(generics.RetrieveAPIView):

    queryset = PlacementCompanyThread.objects.prefetch_related('posts__extracted')
    serializer_class = PlacementCompleteThreadSerializer
    
    lookup_field = 'company_slug'

class PlacementBlogPostListView(generics.ListAPIView):
    serializer_class = PlacementBlogPostSerializer
    pagination_class = InternshipPagination

    def get_queryset(self):
        queryset = PlacementBlogPost.objects.select_related('extracted', 'thread').order_by('-published')
        
        # Frontend should send: ?domain=Software&domain=Design
        domains = self.request.query_params.getlist('domain')
        companies = self.request.query_params.getlist('company')

        # If the list is not empty, filter using __in
        if domains:
            queryset = queryset.filter(extracted__domain__in=domains)
        if companies:
            queryset = queryset.filter(thread__company_slug__in=companies)
            
        return queryset

class PlacementLatestCompanyPostListView(generics.ListAPIView):
    serializer_class = PlacementBlogPostSerializer
    pagination_class = InternshipPagination

    def get_queryset(self):

        latest_post_subquery = PlacementBlogPost.objects.filter(
            thread=OuterRef('thread')
        ).order_by('-published').values('id')[:1]

        #Filter the main PlacementBlogPost table to only include those exact IDs, 
        return PlacementBlogPost.objects.filter(
            id=Subquery(latest_post_subquery)
        ).select_related('extracted').order_by('-published')