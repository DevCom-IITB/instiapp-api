from django.db import models
import uuid
# Create your models here.
class CalendarSourcePreference(models.Model):
    user = models.OneToOneField(
        'users.UserProfile',
        on_delete=models.CASCADE,
        related_name='calendar_preferences'
    )
    show_instiapp_going = models.BooleanField(default=True)
    show_instiapp_followed_bodies = models.BooleanField(default=True)
    show_resobin = models.BooleanField(default=True)
    show_google = models.BooleanField(default=False)    # future
    show_blogs = models.BooleanField(default=False)     # future
    notifications_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendarhub_source_preference'
        
class CalendarBodyPreference(models.Model):
    user = models.ForeignKey(
        'users.UserProfile',
        on_delete=models.CASCADE,
        related_name='calendar_body_preferences'
    )
    body = models.ForeignKey(
        'bodies.Body',
        on_delete=models.CASCADE
    )
    enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendarhub_body_preference'
        unique_together = [('user', 'body')]
        indexes = [
            models.Index(fields=['user', 'enabled']),
        ]

class ExternalCalendarAccount(models.Model):
    class Provider(models.TextChoices):
        RESOBIN = 'resobin', 'ResoBin'
        GOOGLE  = 'google',  'Google'   # future

    class Status(models.TextChoices):
        ACTIVE       = 'active',       'Active'
        DISCONNECTED = 'disconnected', 'Disconnected'
        ERROR        = 'error',        'Error'
        SYNCING      = 'syncing',      'Syncing'

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=Provider.choices)
    external_user_id = models.CharField(max_length=255, blank=True)  # SSO username

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    # For future Google OAuth — not used for ResoBin
    access_token_enc  = models.TextField(blank=True, null=True)
    refresh_token_enc = models.TextField(blank=True, null=True)
    token_expiry      = models.DateTimeField(null=True, blank=True)
    scopes            = models.CharField(max_length=500, blank=True)

    last_sync_at     = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(max_length=20, blank=True)
    last_sync_error  = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendarhub_external_account'
        unique_together = [('user', 'provider')]

class ExternalCalendarSyncState(models.Model):
    account     = models.OneToOneField(
        ExternalCalendarAccount,
        on_delete=models.CASCADE,
        related_name='sync_state'
    )
    sync_token  = models.CharField(max_length=1000, blank=True)
    page_token  = models.CharField(max_length=1000, blank=True)
    etag        = models.CharField(max_length=255, blank=True)
    cursor_json = models.JSONField(null=True, blank=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendarhub_sync_state'

class ExternalCalendarEventCache(models.Model):
    class Provider(models.TextChoices):
        RESOBIN = 'resobin', 'ResoBin'
        GOOGLE  = 'google',  'Google'

    class Subsource(models.TextChoices):
        CLASS    = 'class',    'Class'
        TUTORIAL = 'tutorial', 'Tutorial'
        LAB      = 'lab',      'Lab'
        EXAM     = 'exam',     'Exam'
        DEADLINE = 'deadline', 'Deadline'
        OTHER    = 'other',    'Other'

    id  = models.BigAutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    user     = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=Provider.choices)

    external_event_id    = models.CharField(max_length=255)
    external_calendar_id = models.CharField(max_length=255, blank=True, default='')

    # Normalized fields
    title       = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    location    = models.CharField(max_length=500, blank=True)
    start_time  = models.DateTimeField()   # Always tz-aware (USE_TZ=True)
    end_time    = models.DateTimeField()
    all_day     = models.BooleanField(default=False)
    subsource   = models.CharField(max_length=20, choices=Subsource.choices, default=Subsource.OTHER)
    event_url   = models.URLField(blank=True, null=True)

    raw_payload  = models.JSONField(null=True, blank=True)   # requires MySQL 5.7.8+
    is_cancelled = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
    synced_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'calendarhub_event_cache'
        unique_together = [('user', 'provider', 'external_event_id', 'external_calendar_id')]
        indexes = [
            models.Index(fields=['user', 'provider', 'start_time'],  name='idx_cache_user_prov_start'),
            models.Index(fields=['user', 'provider', 'updated_at'],  name='idx_cache_user_prov_updated'),
            models.Index(fields=['user', 'provider', 'is_cancelled'],name='idx_cache_user_prov_cancel'),
        ]

class SharedCalendar(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name       = models.CharField(max_length=200)
    slug       = models.SlugField(unique=True)        # e.g. "iitb-academic-2025-26"
    description= models.TextField(blank=True)
    color      = models.CharField(max_length=7)        # hex e.g. "#E53935"
    created_by = models.ForeignKey('users.UserProfile', on_delete=models.SET_NULL, null=True)
    is_public  = models.BooleanField(default=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendarhub_shared_calendar'
        indexes = [
            models.Index(fields=['is_active', 'is_public']),
        ]

class SharedCalendarEvent(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    calendar        = models.ForeignKey(SharedCalendar, on_delete=models.CASCADE, related_name='events')
    title           = models.CharField(max_length=500)
    description     = models.TextField(blank=True)
    location        = models.CharField(max_length=500, blank=True)
    start_time      = models.DateTimeField()
    end_time        = models.DateTimeField()
    all_day         = models.BooleanField(default=False)
    recurrence_rule = models.CharField(max_length=500, blank=True)  # iCal RRULE, future use
    is_cancelled    = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendarhub_shared_event'
        indexes = [
            models.Index(fields=['calendar', 'start_time']),
            models.Index(fields=['calendar', 'is_cancelled']),
        ]

class UserSharedCalendarSubscription(models.Model):
    user          = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE)
    calendar      = models.ForeignKey(SharedCalendar, on_delete=models.CASCADE)
    enabled       = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'calendarhub_shared_subscription'
        unique_together = [('user', 'calendar')]
        indexes = [
            models.Index(fields=['user', 'enabled']),
        ]