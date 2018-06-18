from rest_framework import viewsets
from messmenu.models import Hostel

# Create your views here.
class MessMenuViewSet(viewsets.ModelViewSet):
    queryset = Hostel.objects.all()
