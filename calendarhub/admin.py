from django.contrib import admin
from calendarhub import models


@admin.register(models.CalendarSourcePreference)
class CalendarSourcePreferenceAdmin(admin.ModelAdmin):
    list_display  = ['user', 'show_instiapp_going', 'show_instiapp_followed_bodies', 'show_resobin', 'notifications_enabled', 'updated_at']
    list_filter   = ['show_instiapp_going', 'show_instiapp_followed_bodies', 'show_resobin', 'notifications_enabled']
    search_fields = ['user__name', 'user__ldap_id']


@admin.register(models.CalendarBodyPreference)
class CalendarBodyPreferenceAdmin(admin.ModelAdmin):
    list_display  = ['user', 'body', 'enabled', 'updated_at']
    list_filter   = ['enabled']
    search_fields = ['user__name', 'user__ldap_id', 'body__name']
    # raw_id_fields = ['user', 'body']


@admin.register(models.ExternalCalendarAccount)
class ExternalCalendarAccountAdmin(admin.ModelAdmin):
    list_display    = ['user', 'provider', 'external_user_id', 'status'] #'last_sync_at', 'last_sync_status']
    list_filter     = ['provider', 'status']
    search_fields   = ['user__name', 'user__ldap_id', 'external_user_id']
    # readonly_fields = ['last_sync_at', 'created_at', 'updated_at']


@admin.register(models.ExternalCalendarSyncState)
class ExternalCalendarSyncStateAdmin(admin.ModelAdmin):
    list_display    = ['account', 'updated_at']
    search_fields   = ['account__user__name', 'account__external_user_id']
    readonly_fields = ['updated_at']


@admin.register(models.ExternalCalendarEventCache)
class ExternalCalendarEventCacheAdmin(admin.ModelAdmin):
    list_display    = ['user', 'provider', 'subsource', 'title', 'location', 'start_time', 'end_time', 'is_cancelled', 'synced_at']
    list_filter     = ['provider', 'subsource', 'is_cancelled', 'all_day']
    search_fields   = ['user__name', 'user__ldap_id', 'title', 'external_event_id']
    readonly_fields = ['uid', 'synced_at', 'updated_at']
    date_hierarchy  = 'start_time'


@admin.register(models.SharedCalendar)
class SharedCalendarAdmin(admin.ModelAdmin):
    list_display        = ['name', 'slug', 'color', 'created_by', 'is_public', 'is_active', 'created_at']
    list_filter         = ['is_public', 'is_active']
    search_fields       = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields     = ['id', 'created_at', 'updated_at']


@admin.register(models.SharedCalendarEvent)
class SharedCalendarEventAdmin(admin.ModelAdmin):
    list_display    = ['title', 'calendar', 'location', 'start_time', 'end_time', 'all_day', 'is_cancelled']
    list_filter     = ['calendar', 'all_day', 'is_cancelled']
    search_fields   = ['title', 'calendar__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy  = 'start_time'


@admin.register(models.UserSharedCalendarSubscription)
class UserSharedCalendarSubscriptionAdmin(admin.ModelAdmin):
    list_display    = ['user', 'calendar', 'enabled', 'subscribed_at']
    list_filter     = ['enabled', 'calendar']
    search_fields   = ['user__name', 'user__ldap_id', 'calendar__name']
    readonly_fields = ['subscribed_at']
