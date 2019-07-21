"""Views for users app."""
from uuid import UUID
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from login.helpers import update_fcm_device

from events.models import UserEventStatus
from events.models import Event
from events.serializers import EventSerializer
from news.models import UserNewsReaction
from news.models import NewsEntry
from users.serializer_full import UserProfileFullSerializer
from users.models import UserProfile
from users.models import WebPushSubscription
from roles.helpers import login_required_ajax
from roles.helpers import forbidden_no_privileges

class UserProfileViewSet(viewsets.ModelViewSet):
    """UserProfile"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileFullSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def retrieve(self, request, pk):
        try:
            UUID(pk, version=4)
            return super().retrieve(self, request, pk)
        except ValueError:
            queryset = UserProfileFullSerializer.setup_eager_loading(UserProfile.objects)
            profile = get_object_or_404(queryset, ldap_id=pk)
            return Response(UserProfileFullSerializer(
                profile, context={'request': request}).data)

    @login_required_ajax
    def retrieve_me(self, request):
        """Get current user."""
        queryset = UserProfileFullSerializer.setup_eager_loading(UserProfile.objects)
        user_profile = queryset.get(user=request.user)

        # WARNING: DEPREACATED
        # Update fcm id if present
        if 'fcm_id' in request.GET:
            update_fcm_device(request, request.GET['fcm_id'])

        return Response(UserProfileFullSerializer(
            user_profile, context=self.get_serializer_context()).data)

    @login_required_ajax
    def update_me(self, request):
        """Update current user."""
        # Create device instead of updating profile
        if 'fcm_id' in request.data:
            update_fcm_device(request, request.data.pop('fcm_id', None))

        # Check if all fields are exposed ones
        if any(f not in UserProfile.ExMeta.user_editable for f in request.data):
            return forbidden_no_privileges()

        # Count as a ping
        profile = request.user.profile
        profile.last_ping = timezone.now()
        profile.active = True

        serializer = UserProfileFullSerializer(
            profile, data=request.data, context=self.get_serializer_context())
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response(serializer.data)

    @classmethod
    @login_required_ajax
    def set_ues_me(cls, request, event_pk):
        """Set UES for current user.
        This will create or update if record exists."""

        # Get status from query paramter
        status = request.GET.get('status')
        if status is None:
            return Response({"message": "status is required"}, status=400)
        status = int(status)

        # Try to get existing UES
        ues = UserEventStatus.objects.filter(event__id=event_pk, user=request.user.profile).first()

        # Delete record if unknown status
        if status not in (1, 2):
            if ues:
                ues.delete()
            return Response(status=204)

        # Create new UserEventStatus if not existing
        if not ues:
            get_event = get_object_or_404(Event.objects.all(), pk=event_pk)
            UserEventStatus.objects.create(
                event=get_event, user=request.user.profile, status=status)
            return Response(status=204)

        # Update existing UserEventStatus
        ues.status = status
        ues.save()
        return Response(status=204)

    @classmethod
    @login_required_ajax
    def set_unr_me(cls, request, news_pk):
        """Set UNR(User News Reaction) for current user.
        This will create or update if record exists."""

        # Get reaction from query parameter
        reaction = request.GET.get('reaction')
        if reaction is None:
            return Response({"message": "reaction is required"}, status=400)

        # Get existing record if it exists
        unr = UserNewsReaction.objects.filter(news__id=news_pk, user=request.user.profile).first()

        # Create new UserNewsReaction if not existing
        if not unr:
            get_news = get_object_or_404(NewsEntry.objects.all(), pk=news_pk)
            UserNewsReaction.objects.create(
                news=get_news, user=request.user.profile, reaction=reaction)
            return Response(status=204)

        # Update existing UserNewsReaction
        unr.reaction = reaction
        unr.save()
        return Response(status=204)

    @classmethod
    @login_required_ajax
    def get_my_events(cls, request):
        """Current user's created events."""
        events = Event.objects.filter(created_by=request.user.profile)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    @classmethod
    @login_required_ajax
    def subscribe_web_push(cls, request):
        """Subscribe to web push."""
        data = request.data
        sub = request.user.profile.web_push_subscriptions.filter(endpoint=data['endpoint']).first()

        # Create new subscription if not found
        if not sub:
            sub = WebPushSubscription(
                user=request.user.profile,
                endpoint=data['endpoint'],
            )

        # Update values
        sub.p256dh = data['keys']['p256dh']
        sub.auth = data['keys']['auth']
        sub.save()

        return Response(status=204)
