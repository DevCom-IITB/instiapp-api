"""Views for users app."""
from rest_framework import viewsets
from users.serializers import UserProfileFullSerializer
from users.models import UserProfile

class UserProfileViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that allows users to be viewed or edited."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileFullSerializer
