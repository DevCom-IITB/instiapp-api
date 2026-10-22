from rest_framework import generics
from .models import PlacementCompanyThread, PlacementBlogPost
from .serializers import PlacementCompleteThreadSerializer, PlacementBlogPostSerializer
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from roles.helpers import login_required_ajax
from alumni.models import AlumniUser
from helpers.misc import query_search

class InternshipPagination(PageNumberPagination):
    page_size = 20

class FilterOptionsView(APIView):
    # Returns the unique lists of domains and companies 
    @login_required_ajax
    def get(self, request, *args, **kwargs):
        # Block alumni
        user_profile = request.user.profile
        if AlumniUser.objects.filter(ldap=user_profile.ldap_id).exists():
            return Response({"error": "Alumni cannot access this page."}, status=403)
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
    serializer_class = PlacementCompleteThreadSerializer
    pagination_class = InternshipPagination

    @login_required_ajax
    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile
        if AlumniUser.objects.filter(ldap=user_profile.ldap_id).exists():
            return Response({"error": "Alumni cannot access this page."}, status=403)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Start with all threads
        queryset = PlacementCompanyThread.objects.prefetch_related('posts__extracted').order_by('-first_post_date')
        
        # Grab the filters from the URL if they exist
        domains = self.request.query_params.getlist('domain')
        companies = self.request.query_params.getlist('company')
        from_date = parse_date(self.request.query_params.get('from_date', ''))
        to_date = parse_date(self.request.query_params.get('to_date', ''))

        if domains:
            # Use Q objects to search INSIDE the comma-separated strings
            domain_query = Q()
            for d in domains:
                domain_query |= Q(domain__icontains=d.strip())
            queryset = queryset.filter(domain_query)
            
        if companies:
            # Removed the 'thread__' prefix, as we are already on the Thread model
            queryset = queryset.filter(company_slug__in=companies)
        if from_date:
            queryset = queryset.filter(first_post_date__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(first_post_date__date__lte=to_date)
            
        queryset = query_search(self.request, 3, queryset, ["company_name", "role", "domain"], "placement_thread")
        return queryset
    
class PlacementBlogPostListView(generics.ListAPIView):
    serializer_class = PlacementBlogPostSerializer
    pagination_class = InternshipPagination

    @login_required_ajax
    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile
        if AlumniUser.objects.filter(ldap=user_profile.ldap_id).exists():
            return Response({"error": "Alumni cannot access this page."}, status=403)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Removed 'extracted' from select_related
        queryset = PlacementBlogPost.objects.select_related('thread').order_by('-published')
        
        domains = self.request.query_params.getlist('domain')
        companies = self.request.query_params.getlist('company')
        from_date = parse_date(self.request.query_params.get('from_date', ''))
        to_date = parse_date(self.request.query_params.get('to_date', ''))

        if domains:
            # Since we are querying Posts, we look at the connected thread's domain
            domain_query = Q()
            for d in domains:
                domain_query |= Q(thread__domain__icontains=d.strip())
            queryset = queryset.filter(domain_query)
            
        if companies:
            # Keep thread__ here because we are filtering Posts based on their Thread
            queryset = queryset.filter(thread__company_slug__in=companies)
        if from_date:
            queryset = queryset.filter(published__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(published__date__lte=to_date)
            
        queryset = query_search(self.request, 3, queryset, ["raw_company_name", "raw_content"], "placement_post")
        return queryset
