"""Views for achievements models."""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from roles.helpers import (
    login_required_ajax,
    user_has_insti_privilege,
    forbidden_no_privileges,
)


from users.models import UserProfile
from .models import SSOBan
from .serializers import SSOBansSerializer


# Create your views here.


class SSOBanViewSet(viewsets.ModelViewSet):
    queryset = SSOBan.objects.all()
    serializer_class = SSOBansSerializer

    @login_required_ajax
    def list(self, request):
        """List all the banned Accounts."""
        if user_has_insti_privilege(request.user.profile, "RoleB"):
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return forbidden_no_privileges()

    @login_required_ajax
    def retrieve(self, request, pk):
        if user_has_insti_privilege(request.user.profile, "RoleB"):
            instance = get_object_or_404(self.queryset, pk=pk)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return forbidden_no_privileges()

    @login_required_ajax
    def create(self, request):
        if user_has_insti_privilege(request.user.profile, "RoleB"):
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                banned_user = serializer.validated_data.get("banned_user")
                duration_of_ban = serializer.validated_data.get("duration_of_ban")

                if banned_user:
                    banned_user_model = UserProfile.objects.filter(
                        ldap_id=banned_user
                    ).first()
                    if not banned_user_model:
                        return Response(
                            {"user": ["This field is Invalid."]},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                if not duration_of_ban:
                    return Response(
                        {"duration_of_ban": ["This field is required."]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                serializer.validated_date["banned_by"] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return forbidden_no_privileges()

    @login_required_ajax
    def update(self, request,  *args, pk=None, **kwargs):
        if user_has_insti_privilege(request.user.profile, "RoleB"):
            instance = get_object_or_404(self.queryset, pk=pk)
            serializer = self.get_serializer(instance, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.validated_data["banned_by"] = request.user
                serializer.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return forbidden_no_privileges()

    @login_required_ajax
    def destroy(self, request, *args, pk=None, **kwargs):
        if user_has_insti_privilege(request.user.profile, "RoleB"):
            instance = get_object_or_404(self.queryset, pk=pk)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return forbidden_no_privileges()
