from rest_framework.views import APIView
from .serializer import PopUpSerializer
from .models import PopUp, UserPopUpRead
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class PopUpViewSet(APIView):
    """
    Pop Up for the events
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, popup_id=None):
        if popup_id is not None:
            # Get a single popup if an ID is provided in the URL
            popup = get_object_or_404(PopUp, id=popup_id)

            # Check if the user has already read this popup
            if UserPopUpRead.objects.filter(user=request.user.profile, popup=popup).exists():
                return Response(
                    {"error": "Popup has already been read."},
                    status=status.HTTP_409_CONFLICT
                )

            serializer = PopUpSerializer(popup)
            return Response(serializer.data)

        # Get IDs of popups already read by the user
        read_popup_ids = UserPopUpRead.objects.filter(
            user=request.user.profile
        ).values_list('popup_id', flat=True)

        # Fetch active popups that the user has not read
        popups = PopUp.objects.filter(is_active=True).exclude(id__in=read_popup_ids)

        serializer = PopUpSerializer(popups, many=True)
        return Response(serializer.data)

    # def patch(self, request, popup_id=None):
    #     # Authorization check: Only allow staff/admin users to update popups.
    #     if not request.user.is_staff:
    #         return Response(
    #             {"error": "You do not have permission to perform this action."},
    #             status=status.HTTP_403_FORBIDDEN
    #         )

    #     if popup_id is None:
    #         return Response(
    #             {"error": "You must provide a popup ID in the URL to update it."},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     popup = get_object_or_404(PopUp, id=popup_id)

    #     serializer = PopUpSerializer(popup, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
        
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PopUpMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, popup_id=None):
        """
        Marks a specific popup as read for the current user.
        """
        popup = get_object_or_404(PopUp, id=popup_id)
        
        # Create a record to mark this popup as read for this user.
        # get_or_create prevents creating duplicate entries.
        UserPopUpRead.objects.get_or_create(
            user=request.user.profile,
            popup=popup
        )
        return Response({
            "status": "success",
            "detail": f"Popup with ID {popup_id} has been marked as read."
        }, status=status.HTTP_200_OK)