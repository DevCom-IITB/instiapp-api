from rest_framework import serializers
from calendarhub import models

class CalendarSourcePreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CalendarSourcePreference
        fields = [
            'show_instiapp_going',
            'show_instiapp_followed_bodies',
            'show_all_events',
            'show_resobin',
            'notifications_enabled',
            'created_at',
            'updated_at',
        ]


class CalendarBodyPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CalendarBodyPreference
        fields = [
            'user',
            'body',
            'enabled',
            'updated_at',
        ]


class ExternalCalendarAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExternalCalendarAccount
        fields = [
            'id',
            'user',
            'provider',
            'external_user_id',
            'status',
            'scopes',
            # 'token_expiry',
            # 'last_sync_at',
            # 'last_sync_status',
            # 'last_sync_error',
            'created_at',
            'updated_at',
        ]


class ExternalCalendarSyncStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExternalCalendarSyncState
        fields = [
            'page_token',
            'etag',
            'cursor_json',
            'updated_at',
        ]


class ExternalCalendarEventCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExternalCalendarEventCache
        fields = [
            'uid',
            'provider',
            'title',
            'description',
            'location',
            'start_time',
            'end_time',
            'all_day',
            'subsource',
            'event_url',
            'is_cancelled',
            'updated_at',
            'synced_at',
        ]

        
class SharedCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SharedCalendar
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'color',
            'is_public',
            'is_active',
            'created_at',
            'updated_at',
        ]


class SharedCalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SharedCalendarEvent
        fields = [
            'id',
            'calendar',
            'title',
            'description',
            'location',
            'start_time',
            'end_time',
            'all_day',
            'recurrence_rule',
            'is_cancelled',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'calendar', 'created_at', 'updated_at']


class UserSharedCalendarSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserSharedCalendarSubscription
        fields = [
            'calendar',
            'enabled',
            'subscribed_at',
        ]
