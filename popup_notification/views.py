from rest_framework.views import APIView
from other.views import get_notif_queryset
from other.serializers import NotificationSerializer
from roles.helpers import login_required_ajax
from rest_framework.response import Response
# Create your views here.
class PopUpViewSet(APIView):
     @login_required_ajax
     def get(self, request):
        """
        Gets the latest unread notification for the current user.
        Ideal for displaying a single popup.
        """
        
        latest_notification = get_notif_queryset(request.user.notifications).first()

        if not latest_notification:
            return Response(status=204)  # No Content

        serializer = NotificationSerializer(latest_notification)
        serialized_data = serializer.data

        # The actor object contains the details of the event, news, etc.
        actor = serialized_data.get("actor")

        if not actor:
            # Fallback for notifications without a proper actor
            return Response(
                {
                    "verb": serialized_data.get("verb"),
                    "title": "Notification",
                    "description": serialized_data.get("verb"),
                    "imageurl": None,
                    "links": None,
                }
            )

        title = actor.get("name") or actor.get("title")
        
        description = actor.get("description") or actor.get("content")

        if serialized_data.get("actor_type") == "complaintcomment":
            description = actor.get("text")

        # Truncate long descriptions for a clean popup display
        if description and len(description) > 150:
            description = description[:147] + "..."

        image_url = actor.get("image_url")
        
        link = actor.get("website_url") or actor.get("url")

        request_data = {
            "verb": serialized_data.get("verb"),
            "title": title,
            "description": description,
            "imageurl": image_url,
            "links": link,
        }
        return Response(request_data)

class MarkLatestAsReadView(APIView):
    @login_required_ajax
    def post(self, request):
        """
        Finds the latest unread notification for the user and marks it as read.
        """
        latest_notification = get_notif_queryset(request.user.notifications).first()

        if not latest_notification:
            return Response(status=204)  # No Content

        # Mark as read
        latest_notification.unread = False
        latest_notification.save()

        return Response(status=204)
