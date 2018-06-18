"""Views for mess menu."""
from rest_framework.response import Response
from rest_framework.decorators import api_view
from messmenu.models import Hostel
from messmenu.serializers import HostelSerializer

@api_view(['GET', ])
def get_mess(request):
    """Get mess menus of all hostels."""
    queryset = Hostel.objects.all()
    return Response(HostelSerializer(queryset, many=True).data)
