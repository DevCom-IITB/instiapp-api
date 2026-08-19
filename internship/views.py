from rest_framework import generics
from .models import CompanyThread, BlogPost
from .serializers import CompanyThreadSerializer, CompleteThreadSerializer, BlogPostSerializer
from django.db.models import OuterRef, Subquery
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from roles.helpers import login_required_ajax
from alumni.models import AlumniUser
from helpers.misc import query_search
class InternshipPagination(PageNumberPagination):
    page_size = 20

class FilterOptionsView(APIView):
    #Returns the unique lists of domains, categories, and companies 
    @login_required_ajax
    def get(self, request, *args, **kwargs):
        # Block alumni
        user_profile = request.user.profile
        if AlumniUser.objects.filter(ldap=user_profile.ldap_id).exists():
            return Response({"error": "Alumni cannot access this page."}, status=403)
        # .exclude() drops empty values, .distinct() removes duplicates
        domains = CompanyThread.objects.exclude(domain__isnull=True).exclude(domain="").values_list('domain', flat=True).distinct().order_by('domain')
        categories = CompanyThread.objects.exclude(category__isnull=True).exclude(category="").values_list('category', flat=True).distinct().order_by('category')
        companies = CompanyThread.objects.values('company_name', 'company_slug').distinct().order_by('company_name')

        # Return a simple dictionary for the frontend
        return Response({
            "domains": list(domains),
            "categories": list(categories),
            "companies": list(companies)
        })

class ThreadListView(generics.ListAPIView):
    serializer_class = CompanyThreadSerializer
    pagination_class = InternshipPagination

    @login_required_ajax
    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile
        if AlumniUser.objects.filter(ldap=user_profile.ldap_id).exists():
            return Response({"error": "Alumni cannot access this page."}, status=403)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Start with all threads
        queryset = CompanyThread.objects.all().order_by('-first_post_date')
        
        # Grab the filters from the URL if they exist
        domains = self.request.query_params.getlist('domain')
        categories = self.request.query_params.getlist('category')
        companies = self.request.query_params.getlist('company')

        # If the list is not empty, filter using __in
        if domains:
            queryset = queryset.filter(extracted__domain__in=domains)
        if categories:
            queryset = queryset.filter(extracted__category__in=categories)
        if companies:
            queryset = queryset.filter(thread__company_slug__in=companies)
            
        queryset = query_search(self.request, 3, queryset, ["company_name", "role", "domain"], "internship_thread")
        return queryset
    
class ThreadDetailView(generics.RetrieveAPIView):

    queryset = CompanyThread.objects.prefetch_related('posts__extracted')
    serializer_class = CompleteThreadSerializer
    
    lookup_field = 'company_slug'

    @login_required_ajax
    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile
        if AlumniUser.objects.filter(ldap=user_profile.ldap_id).exists():
            return Response({"error": "Alumni cannot access this page."}, status=403)
        return super().get(request, *args, **kwargs)

class BlogPostListView(generics.ListAPIView):
    serializer_class = BlogPostSerializer
    pagination_class = InternshipPagination

    @login_required_ajax
    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile
        if AlumniUser.objects.filter(ldap=user_profile.ldap_id).exists():
            return Response({"error": "Alumni cannot access this page."}, status=403)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = BlogPost.objects.select_related('extracted', 'thread').order_by('-published')
        
        # Frontend should send: ?domain=Software&domain=Design
        domains = self.request.query_params.getlist('domain')
        categories = self.request.query_params.getlist('category')
        companies = self.request.query_params.getlist('company')

        # If the list is not empty, filter using __in
        if domains:
            queryset = queryset.filter(extracted__domain__in=domains)
        if categories:
            queryset = queryset.filter(extracted__category__in=categories)
        if companies:
            queryset = queryset.filter(thread__company_slug__in=companies)
            
        queryset = query_search(self.request, 3, queryset, ["raw_company_name", "raw_content"], "internship_post")
        return queryset

class LatestCompanyPostListView(generics.ListAPIView):
    serializer_class = BlogPostSerializer
    pagination_class = InternshipPagination

    @login_required_ajax
    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile
        if AlumniUser.objects.filter(ldap=user_profile.ldap_id).exists():
            return Response({"error": "Alumni cannot access this page."}, status=403)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):

        latest_post_subquery = BlogPost.objects.filter(
            thread=OuterRef('thread')
        ).order_by('-published').values('id')[:1]

        #Filter the main BlogPost table to only include those exact IDs, 
        queryset = BlogPost.objects.filter(
            id=Subquery(latest_post_subquery)
        ).select_related('extracted').order_by('-published')
        queryset = query_search(self.request, 3, queryset, ["raw_company_name", "raw_content"], "internship_post")
        return queryset