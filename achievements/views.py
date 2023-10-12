"""Views for achievements models."""
from uuid import UUID
import pyotp
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from roles.helpers import login_required_ajax
from roles.helpers import forbidden_no_privileges
from roles.helpers import user_has_privilege

from achievements.models import Achievement, Interest, UserInterest, Skill
from achievements.models import OfferedAchievement
from achievements.serializers import AchievementSerializer, UserInterestSerializer
from achievements.serializers import AchievementUserSerializer
from achievements.serializers import OfferedAchievementSerializer

from users.serializers import UserProfileSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    """Views for Achievements"""

    queryset = Achievement.objects
    serializer_class = AchievementUserSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    @login_required_ajax
    def list(self, request):
        """List the user's achivements and requests."""

        self.queryset = AchievementSerializer.setup_eager_loading(self.queryset)
        self.queryset = self.queryset.filter(user=request.user.profile)

        serializer = AchievementSerializer(
            self.queryset, many=True, context={"request": request}
        )

        return Response(serializer.data)

    @login_required_ajax
    def list_body(self, request, pk):
        """List the user's achivements and requests."""

        if not user_has_privilege(request.user.profile, pk, "VerA"):
            return forbidden_no_privileges()

        self.queryset = AchievementUserSerializer.setup_eager_loading(self.queryset)
        self.queryset = self.queryset.filter(body__id=pk, dismissed=False)

        serializer = AchievementUserSerializer(
            self.queryset, many=True, context={"request": request}
        )

        return Response(serializer.data)

    @login_required_ajax
    def create(self, request):
        """Make a request to a body for a new achievement."""
        if request.data["isSkill"]:
            skill = Skill.objects.filter(title=request.data["title"]).first()
            if skill:
                request.data["body"] = skill.body.id
                request.data["description"] = ""
            else:
                return forbidden_no_privileges()

        # Disallow requests without body
        if ("body" not in request.data or not request.data["body"]) and (
            not request.data["isSkill"]
        ):
            return forbidden_no_privileges()

        return super().create(request)

    @login_required_ajax
    def update(self, request, pk):
        """Update/Verify an achievement.
        Needs BodyRole with `VerA` or can patch own achievement"""

        # Get the achievement currently in database
        achievement = get_object_or_404(self.queryset, id=pk)

        # Check if this is a patch request and the user is patching
        if request.method == "PATCH" and request.user.profile == achievement.user:
            achievement.hidden = bool(request.data["hidden"])
            achievement.save(update_fields=["hidden"])
            return Response(status=204)

        # Check if the user has privileges for updating
        if not user_has_privilege(request.user.profile, achievement.body.id, "VerA"):
            return forbidden_no_privileges()

        # Prevent achievements without any body
        if (
            "body" not in request.data
            or not request.data["body"]
            or request.data["body"] != str(achievement.body.id)
        ):
            return Response(
                {
                    "message": "invalid body",
                    "detail": "The body for this achievement is changed or invalid.",
                },
                status=400,
            )

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


class OfferedAchievementViewSet(viewsets.ModelViewSet):
    """Views for Achievement Offers"""

    queryset = OfferedAchievement.objects
    serializer_class = OfferedAchievementSerializer

    @login_required_ajax
    def retrieve(self, request, pk):
        """Get a achievement offer."""

        # Get current object
        offer = get_object_or_404(self.queryset, id=pk)
        data = OfferedAchievementSerializer(offer).data

        # Extra fields in user serializer
        extra_fields = []

        # Query for getting users
        query = offer.achievements.filter(verified=True).prefetch_related("user")

        # Check for verification privilege
        if user_has_privilege(request.user.profile, offer.body.id, "VerA"):
            data["secret"] = offer.secret

            # Add extra fields for privileged users
            extra_fields = [
                "roll_no",
                "email",
                "contact_no",
                "department_name",
                "degree",
            ]
        else:
            # Filter out hidden achievements
            query = query.filter(hidden=False)

        # Get users haveing this achievement
        users = [a.user for a in query]
        data["users"] = UserProfileSerializer(
            users, many=True, context={"extra": extra_fields}
        ).data

        return Response(data)

    @login_required_ajax
    def create(self, request):
        """Offer a new achievement for an event."""

        # Check for event add privilege
        if not user_has_privilege(request.user.profile, request.data["body"], "AddE"):
            return forbidden_no_privileges()

        return super().create(request)

    @login_required_ajax
    def update(self, request, pk):
        """Update an offered achievement."""

        # Get current object
        offer = get_object_or_404(self.queryset, id=pk)

        # Check for event add privilege
        if not user_has_privilege(request.user.profile, offer.body.id, "AddE"):
            return forbidden_no_privileges()

        return super().update(request, pk)

    @login_required_ajax
    def destroy(self, request, pk):
        """Update an offered achievement."""

        # Get current object
        offer = get_object_or_404(self.queryset, id=pk)

        # Check for event add privilege
        if not user_has_privilege(request.user.profile, offer.body.id, "AddE"):
            return forbidden_no_privileges()

        return super().destroy(request, pk)

    @login_required_ajax
    def claim_secret(self, request, pk):
        """Claim and try to get an achievement with its secret."""

        # Get object
        offer = get_object_or_404(self.queryset, id=pk)

        # Check if secret is valid
        secret = request.data["secret"]
        if offer.secret and (
            secret == offer.secret or secret == pyotp.TOTP(offer.secret).now()
        ):
            if request.user.profile.achievements.filter(offer=offer).exists():
                return Response({"message": "You already have this achievement!"})

            # Create the achievement
            Achievement.objects.create(
                title=offer.title,
                description=offer.description,
                admin_note="SECRET",
                body=offer.body,
                event=offer.event,
                verified=True,
                dismissed=True,
                user=request.user.profile,
                offer=offer,
            )

            return Response({"message": "Achievement unlocked successfully!"}, 201)

        return forbidden_no_privileges()


class UserInterestViewSet(viewsets.ModelViewSet):
    """Views for User Interests"""

    queryset = UserInterest.objects
    serializer_class = UserInterestSerializer

    @login_required_ajax
    def delete(self, request, pk):
        """Delete a user interest."""

        interest = self.queryset.filter(user=request.user.profile, title=pk).first()
        if interest:
            interest.delete()
            return Response({"message": "Interest Deleted Successfully"}, 201)

        return Response({"message": "Interest Doesn't Exist"}, 404)

    @login_required_ajax
    def create(self, request):
        """Add a user interest."""

        try:
            UUID(request.data["id"], version=4)
            interest = get_object_or_404(Interest.objects, id=request.data["id"])
            if self.queryset.filter(
                user=request.user.profile, title=request.data["title"]
            ).exists():
                return Response({"message": "You already have this interest!"}, 400)

            userInterest = UserInterest.objects.create(
                user=request.user.profile, title=interest.title
            )
            userInterest.save()

            return Response({"message": "Interest Added Successfully"}, 201)
        except ValueError:
            return Response({"message": "Invalid ID"}, 404)
