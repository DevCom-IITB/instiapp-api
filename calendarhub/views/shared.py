from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from calendarhub.models import (
    SharedCalendar,
    SharedCalendarEvent,
    UserSharedCalendarSubscription,
)
from calendarhub.serializers import (
    SharedCalendarSerializer,
    SharedCalendarEventSerializer
)
from calendarhub.tasks.signals import creater_approved


class sharedCalendarInfoView(APIView):
    permission_classes = [IsAuthenticated]

    # GET /api/calendar/shared/
    # GET /api/calendar/shared/<slug>/
    # GET /api/calendar/shared/<slug>/events/<uuid:id>/
    def get(self, request, slug=None, event_id=None):
        if event_id is not None:
            # Get a single event
            calendar = get_object_or_404(SharedCalendar, slug=slug)
            event = get_object_or_404(SharedCalendarEvent, id=event_id, calendar=calendar)
            serializer = SharedCalendarEventSerializer(event)
            return Response(serializer.data)

        if slug is None: # List all public calendars
            calendars = SharedCalendar.objects.filter(is_active=True, is_public=True)
            data = SharedCalendarSerializer(calendars, many=True).data

            # Get the set of calendar slugs the user is subscribed to
            subscribed_slugs = set(
                UserSharedCalendarSubscription.objects.filter(
                    user=request.user.profile, calendar__in=calendars
                ).values_list("calendar__slug", flat=True)
            )

            # Add the 'subscribed' status to each calendar dictionary
            for calendar_data in data:
                calendar_data["subscribed"] = calendar_data["slug"] in subscribed_slugs

            return Response(data)

        calendar = get_object_or_404(SharedCalendar, slug=slug, is_active=True) # Get calendar details
        upcoming = (
            SharedCalendarEvent.objects
            .filter(calendar=calendar, start_time__gte=now(), is_cancelled=False)
            .order_by('start_time')
        )
        data = SharedCalendarSerializer(calendar).data
        data['upcoming_events'] = SharedCalendarEventSerializer(upcoming, many=True).data
        data['subscribed'] = UserSharedCalendarSubscription.objects.filter(
            user=request.user.profile, calendar=calendar
        ).exists()
        return Response(data)

    # POST /api/calendar/shared/           → create calendar
    # POST /api/calendar/shared/<slug>/events/  → add event
    def post(self, request, slug=None):
        if not request.user.is_staff:
            return Response({'error': 'Only admins can perform this action'}, status=status.HTTP_403_FORBIDDEN)

        if slug is None:
            serializer = SharedCalendarSerializer(data=request.data)
            if serializer.is_valid():
                calendar_instance = serializer.save(created_by=request.user.profile)

                # Check for 'add_subscriptions' query param to bulk subscribe all users
                flag_str = request.query_params.get('add_subscriptions', 'false')
                if flag_str.lower() == 'true':
                    # The signal receiver expects 'created=True'
                    creater_approved.send(sender=SharedCalendar, instance=calendar_instance, created=True)

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        calendar = get_object_or_404(SharedCalendar, slug=slug)
        serializer = SharedCalendarEventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save(calendar=calendar)
            _schedule_reminders_for_event(event, calendar)
            return Response(SharedCalendarEventSerializer(event).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH /api/calendar/shared/<slug>/           → edit calendar
    # PATCH /api/calendar/shared/<slug>/events/<id>/  → edit event
    def patch(self, request, slug=None, event_id=None):
        if not request.user.is_staff:
            return Response({'error': 'Only admins can perform this action'}, status=status.HTTP_403_FORBIDDEN)

        if event_id is None:
            calendar = get_object_or_404(SharedCalendar, slug=slug)
            serializer = SharedCalendarSerializer(calendar, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        calendar = get_object_or_404(SharedCalendar, slug=slug)
        event = get_object_or_404(SharedCalendarEvent, id=event_id, calendar=calendar)
        serializer = SharedCalendarEventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /api/calendar/shared/<slug>/events/<id>/  → cancel event
    def delete(self, request, slug=None, event_id=None):
        if not request.user.is_staff:
            return Response({'error': 'Only admins can perform this action'}, status=status.HTTP_403_FORBIDDEN)

        calendar = get_object_or_404(SharedCalendar, slug=slug)
        event = get_object_or_404(SharedCalendarEvent, id=event_id, calendar=calendar)
        event.is_cancelled = True
        event.save(update_fields=['is_cancelled'])
        _revoke_reminders_for_event(event, calendar)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UseCalendarSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    # POST /api/calendar/shared/<slug>/subscribe/
    # POST /api/calendar/shared/<slug>/unsubscribe/
    def post(self, request, slug=None):
        calendar = get_object_or_404(SharedCalendar, slug=slug, is_active=True)
        user = request.user.profile

        # Distinguish subscribe vs unsubscribe from the URL path
        if 'unsubscribe' in request.path:
            _revoke_upcoming_reminders_for_user(user, calendar)
            UserSharedCalendarSubscription.objects.filter(user=user, calendar=calendar).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        sub, created = UserSharedCalendarSubscription.objects.get_or_create(
            user=user, calendar=calendar, defaults={'enabled': True}
        )
        if not created:
            sub.enabled = True
            sub.save(update_fields=['enabled'])
        _schedule_upcoming_reminders_for_user(user, calendar)
        return Response({'subscribed': True})

    # PATCH /api/calendar/shared/<slug>/toggle/
    def patch(self, request, slug=None):
        calendar = get_object_or_404(SharedCalendar, slug=slug)
        user = request.user.profile
        enabled = request.data.get('enabled')
        if enabled is None:
            return Response({'error': 'enabled field is required'}, status=status.HTTP_400_BAD_REQUEST)
        UserSharedCalendarSubscription.objects.filter(user=user, calendar=calendar).update(enabled=enabled)
        return Response({'enabled': enabled})



def _schedule_reminders_for_event(event, calendar):
    from calendarhub.tasks.notifications import schedule_reminder
    for user_id in UserSharedCalendarSubscription.objects.filter(calendar=calendar, enabled=True).values_list('user_id', flat=True):
        schedule_reminder(
            event_uid=f'shared:{calendar.slug}:{event.id}',
            user_id=str(user_id),
            start_time=event.start_time,
            title=event.title,
            source='shared',
        )


def _revoke_reminders_for_event(event, calendar):
    from calendarhub.tasks.notifications import cancel_reminder
    for user_id in UserSharedCalendarSubscription.objects.filter(calendar=calendar, enabled=True).values_list('user_id', flat=True):
        cancel_reminder(event_uid=f'shared:{calendar.slug}:{event.id}', user_id=str(user_id))


def _schedule_upcoming_reminders_for_user(user, calendar):
    from calendarhub.tasks.notifications import schedule_reminder
    for event in SharedCalendarEvent.objects.filter(calendar=calendar, start_time__gt=now(), is_cancelled=False):
        schedule_reminder(
            event_uid=f'shared:{calendar.slug}:{event.id}',
            user_id=str(user.id),
            start_time=event.start_time,
            title=event.title,
            source='shared',
        )


def _revoke_upcoming_reminders_for_user(user, calendar):
    from calendarhub.tasks.notifications import cancel_reminder
    for event in SharedCalendarEvent.objects.filter(calendar=calendar, start_time__gt=now(), is_cancelled=False):
        cancel_reminder(event_uid=f'shared:{calendar.slug}:{event.id}', user_id=str(user.id))