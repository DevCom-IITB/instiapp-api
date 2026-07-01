from rest_framework import generics
from .models import CompanyThread
from .serializers import CompanyThreadSerializer, CompleteThreadSerializer

class ThreadListView(generics.ListAPIView):

    queryset = CompanyThread.objects.all().order_by('-first_post_date')
    serializer_class = CompanyThreadSerializer
    
    # Can do pagination too

class ThreadDetailView(generics.RetrieveAPIView):

    queryset = CompanyThread.objects.prefetch_related('posts__extracted')
    serializer_class = CompleteThreadSerializer
    
    lookup_field = 'company_slug'