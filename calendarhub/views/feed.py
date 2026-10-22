from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
from rest_framework import status
from calendarhub.models import CalendarBodyPreference
import json
from events.models import UserEventStatus, Event
from calendarhub.services.cache import get_preferences, get_month_buckets
from calendarhub.services.aggregator import (
    normalize_instiapp_event,
    get_resobin_events,
    get_shared_events,
    dedupe_instiapp,
    overlaps,
    # maybe_enqueue_resobin_sync,
    month_bounds,
)

MAX_WINDOW = 90

class FeedView(APIView):
    """View class for the Feed"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
       # checking the requesting days are valid
       str_date = request.query_params.get('start')
       end_date = request.query_params.get('end')
       if not str_date or not end_date:
           return Response(
                {'error': 'start and end are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

       try:
           start = datetime.fromisoformat(str_date).date()
           end = datetime.fromisoformat(end_date).date()
       except ValueError:
           return Response(
                {'error': 'start and end must be valid ISO dates (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )

       if end < start or (end - start).days > MAX_WINDOW:
           return Response(
                {'error': f'date range must be between 0 and {MAX_WINDOW} days'},
                status=status.HTTP_400_BAD_REQUEST
            )
       items = self.build_feed(request.user.profile, start, end, tz=None)
       return Response({
           'items': items,
           'meta': {
               'window': {
                   'start': str_date,
                   'end':   end_date,
               },
            #    'source_status': source_status,
               'partial_errors': [],
           }
       })

    def get_instiapp_going(self, user, month):
       month_start, month_end = month_bounds(month)
       statuses = UserEventStatus.objects.filter(
        user=user,
        status__in=[1, 2],  # Interested or Going
        event__start_time__lt=month_end,
        event__end_time__gt=month_start,
        ).select_related('event').prefetch_related('event__bodies')

       return [normalize_instiapp_event(s.event, subsource='going') for s in statuses]
    

    def get_instiapp_bodies(self, user, month, exclude_body_ids):
       month_start, month_end = month_bounds(month)
       followed_body_ids = user.followed_bodies.values_list('id', flat=True)
       active_body_ids = [b for b in followed_body_ids if b not in exclude_body_ids]

       events = Event.objects.filter(
        bodies__id__in=active_body_ids,
        start_time__lt=month_end,
        end_time__gt=month_start,
       ).distinct().prefetch_related('bodies')

       return [normalize_instiapp_event(e, subsource='followed_body') for e in events]
    

    def get_all_instiapp_events(self, month):
       month_start, month_end = month_bounds(month)
       events = Event.objects.filter(
        email_rejected=False,
        start_time__lt=month_end,
        end_time__gt=month_start,
       ).distinct().prefetch_related('bodies')

       return [normalize_instiapp_event(e, subsource='all_events') for e in events]
    

    def build_feed(self, user, start, end, tz):
     # 1. Load preferences (from Redis or DB)
      prefs = get_preferences(user)

     # 2. Decompose into month buckets for Redis lookup
      months = get_month_buckets(start, end)  # e.g. ['2026-04', '2026-05', '2026-06']

      items = []
    #   source_status = {}

     # 3. For each month bucket
      for month in months:
          
       
          month_items = []

          if prefs.show_all_events:
            month_items.extend(self.get_all_instiapp_events(month))
          else:
            if prefs.show_instiapp_going:
              month_items.extend(self.get_instiapp_going(user, month))

            if prefs.show_instiapp_followed_bodies:
              disabled_body_ids = CalendarBodyPreference.objects.filter(
                  user=user, enabled=False
              ).values_list('body_id', flat=True)
              month_items.extend(self.get_instiapp_bodies(user, month, exclude_body_ids=disabled_body_ids))

          if prefs.show_resobin:
            month_items.extend(get_resobin_events(user, month))

        # Always include subscribed shared calendars
          month_items.extend(get_shared_events(user, month))

        # Deduplicate InstiApp events that appear via both Going and Body
          month_items = dedupe_instiapp(month_items)

        
          items.extend(month_items)

     # 4. Check ResoBin freshness, enqueue sync if stale
     
    #   if not resobin_fresh:
    #       try:
    #           sync_enqueued = maybe_enqueue_resobin_sync(user)
    #       except Exception:
    #           sync_enqueued = False
    #       source_status['resobin'] = {'status': 'stale', 'sync_enqueued': sync_enqueued}
    #   else:
    #       source_status['resobin'] = {'status': 'fresh'}

     # 5. Filter to exact [start, end], sort, return
      items = [i for i in items if overlaps(i, start, end)]
      items.sort(key=lambda x: x['start_time'])

      return items