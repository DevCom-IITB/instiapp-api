from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import complaints

class ComplaintViewSet(viewsets.ViewSet):
    queryset = complaints.objects.all()

    def list(self, request):

        pass

    def retrieve(self, request, pk):
        pass

    def create(self,request):
        pass

    def search(self, request):
        pass

    def analyze(self, request):
        pass

    def analyze_text(self, request):
        pass