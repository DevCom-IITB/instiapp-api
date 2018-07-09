"""Views that don't fit anywhere else."""
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets

from bodies.models import Body
from bodies.serializer_min import BodySerializerMin
from events.models import Event
from events.serializers import EventSerializer
from events.prioritizer import get_prioritized
from users.models import UserProfile
from users.serializers import UserProfileSerializer

class OtherViewset(viewsets.ViewSet):

    @staticmethod
    def search(request):
        """EXPENSIVE: Search with query param `query` throughout the database."""

        req_query = request.GET.get("query")
        if not req_query or len(req_query) < 3:
            return Response({"message": "No query or too short!"}, status=400)

        # Search bodies by name and description
        bodies = Body.objects.filter(
            Q(name__icontains=req_query) | Q(description__icontains=req_query))

        # Search events by name and description
        events = get_prioritized(Event.objects.filter(
            Q(name__icontains=req_query) | Q(description__icontains=req_query)), request)

        # Search users by only name: don't add anything else here
        users = UserProfile.objects.filter(
            Q(name__icontains=req_query))

        return Response({
            "bodies": BodySerializerMin(bodies, many=True).data,
            "events": EventSerializer(events, many=True).data,
            "users": UserProfileSerializer(users, many=True).data
        })
