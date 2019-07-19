"""Views for achievements models."""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from roles.helpers import login_required_ajax
from roles.helpers import forbidden_no_privileges
from roles.helpers import user_has_privilege

from achievements.models import Achievement
from achievements.serializers import AchievementSerializer
from achievements.serializers import AchievementUserSerializer

class AchievementViewSet(viewsets.ModelViewSet):
    """Views for Achievements"""
    queryset = Achievement.objects
    serializer_class = AchievementUserSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    @login_required_ajax
    def list(self, request):
        """List the user's achivements and requests."""

        self.queryset = AchievementSerializer.setup_eager_loading(self.queryset)
        self.queryset = self.queryset.filter(user=request.user.profile)

        serializer = AchievementSerializer(
            self.queryset, many=True, context={'request': request})

        return Response(serializer.data)

    @login_required_ajax
    def list_body(self, request, pk):
        """List the user's achivements and requests."""

        if not user_has_privilege(request.user.profile, pk, "VerA"):
            return forbidden_no_privileges()

        self.queryset = AchievementUserSerializer.setup_eager_loading(self.queryset)
        self.queryset = self.queryset.filter(body__id=pk, dismissed=False)

        serializer = AchievementUserSerializer(
            self.queryset, many=True, context={'request': request})

        return Response(serializer.data)

    @login_required_ajax
    def create(self, request):
        """Make a request to a body for a new achievement."""

        # Disallow requests without body
        if 'body' not in request.data or not request.data['body']:
            return forbidden_no_privileges()

        return super().create(request)

    @login_required_ajax
    def update(self, request, pk):
        """Update/Verify an achievement.
        Needs BodyRole with `VerA`"""

        # Get the achievement currently in database
        achievement = get_object_or_404(self.queryset, id=pk)

        # Check if the user has privileges for updating
        if not user_has_privilege(request.user.profile, achievement.body.id, "VerA"):
            return forbidden_no_privileges()

        # Prevent achievements without any body
        if 'body' not in request.data or not request.data['body'] or request.data['body'] != str(achievement.body.id):
            return Response({
                "message": "invalid body",
                "detail": "The body for this achievement is changed or invalid."
            }, status=400)

        return super().update(request, pk)

    @login_required_ajax
    def destroy(self, request, pk):
        """Delete an achievement or request.
        Needs BodyRole with `VerA`"""

        # Get the achievement currently in database
        achievement = get_object_or_404(self.queryset, id=pk)

        # Check for permission
        if not user_has_privilege(request.user.profile, achievement.body.id, "VerA"):
            return forbidden_no_privileges()

        return super().destroy(request, pk)
