"""Login Viewset."""
from django.contrib.auth import logout
from rest_framework import viewsets
from rest_framework.response import Response
from login.helpers import perform_login
from users.models import UserProfile
from users.serializer_full import UserProfileFullSerializer

# pylint: disable=C0301

class LoginViewSet(viewsets.ViewSet):
    """Login"""

    @staticmethod
    def login(request):
        """Log in.
        Uses the `code` and `redir` query parameters."""

        # Check if we have the auth code
        auth_code = request.GET.get('code')
        if auth_code is None:
            return Response({"message" : "{?code} is required"}, status=400)

        # Construt post data to get token
        redir = request.GET.get('redir')
        if redir is None:
            return Response({"message" : "{?redir} is required"}, status=400)

        return perform_login(auth_code, redir, request)

    @staticmethod
    def get_user(request):
        """Get session and profile."""

        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({"message":"not logged in"}, status=401)

        # Check if the user has a profile
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            profile_serialized = UserProfileFullSerializer(
                user_profile, context={'request': request})
        except UserProfile.DoesNotExist:
            return Response({'message': "UserProfile doesn't exist"}, status=500)

        # Return the details and nested profile
        return Response({
            'sessionid': request.session.session_key,
            'user': request.user.username,
            'profile_id': user_profile.id,
            'profile': profile_serialized.data
        })

    @staticmethod
    def logout(request):
        """Log out."""

        logout(request)
        return Response({'message': 'logged out'})
