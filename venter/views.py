from coreapi.exceptions import ParseError
from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import detail_route, action

from .models import complaints
from .serializers import ComplaintSerializer, ComplaintPostSerializer
from rest_framework.generics import ListAPIView
from rest_framework import viewsets


class ComplaintViewSet(ListAPIView):
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        if 'created_by__ldap_id' in self.kwargs:
            return complaints.objects.filter(created_by__ldap_id=self.kwargs['created_by__ldap_id'])
        else:
            return complaints.objects.all()


class ComplaintPostViewSet(viewsets.ModelViewSet):
    queryset = complaints.objects.all()
    serializer_class = ComplaintPostSerializer

    def create(self, request):
        return super().create(request)
