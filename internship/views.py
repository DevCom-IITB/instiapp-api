from rest_framework import generics
from .models import CompanyThread, BlogPost
from .serializers import CompleteThreadSerializer, BlogPostSerializer
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
    serializer_class = CompleteThreadSerializer
    pagination_class = InternshipPagination

    @login_required_ajax
    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile
        if AlumniUser.objects.filter(ldap=user_profile.ldap_id).exists():
            return Response({"error": "Alumni cannot access this page."}, status=403)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Start with all threads
        queryset = CompanyThread.objects.prefetch_related('posts__extracted').order_by('-first_post_date')
        
        # Grab the filters from the URL if they exist
        domains = self.request.query_params.getlist('domain')
        categories = self.request.query_params.getlist('category')
        companies = self.request.query_params.getlist('company')
        from_date = parse_date(self.request.query_params.get('from_date', ''))
        to_date = parse_date(self.request.query_params.get('to_date', ''))

        # If the list is not empty, filter using __in
        if domains:
            queryset = queryset.filter(domain__in=domains)
        if categories:
            queryset = queryset.filter(category__in=categories)
        if companies:
            queryset = queryset.filter(company_slug__in=companies)
        if from_date:
            queryset = queryset.filter(first_post_date__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(first_post_date__date__lte=to_date)
            
        queryset = query_search(self.request, 3, queryset, ["company_name", "role", "domain"], "internship_thread")
        return queryset
    
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
        from_date = parse_date(self.request.query_params.get('from_date', ''))
        to_date = parse_date(self.request.query_params.get('to_date', ''))

        # If the list is not empty, filter using __in
        if domains:
            queryset = queryset.filter(extracted__domain__in=domains)
        if categories:
            queryset = queryset.filter(extracted__category__in=categories)
        if companies:
            queryset = queryset.filter(thread__company_slug__in=companies)
        if from_date:
            queryset = queryset.filter(published__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(published__date__lte=to_date)
            
        queryset = query_search(self.request, 3, queryset, ["raw_company_name", "raw_content"], "internship_post")
        return queryset
