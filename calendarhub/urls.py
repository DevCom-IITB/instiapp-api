"""Urls for the calendar integration"""
from django.urls import path
from .views.preferences import CalendarPreferenceView, CalendarBodyPreferenceListView, CalendarBodyPreferenceDetailView
# from .views.resobin import ResobinsyncronizerView
from .views.feed import FeedView
from .views.shared import sharedCalendarInfoView,UseCalendarSubscriptionView


urlpatterns=[
    path(
        "calendar/preferences/", CalendarPreferenceView.as_view(), name='calendar-preferences'
    ),
    path(
        "calendar/preferences/bodies/", CalendarBodyPreferenceListView.as_view(), name='calendar-body-preferences'
    ),
    path(
        "calendar/preferences/bodies/<uuid:body_id>/", CalendarBodyPreferenceDetailView.as_view(), name='calendar-body-preference-detail'
    ),
    # path(
    #     "calendar/resobin/sync-now/",ResobinsyncronizerView.as_view(),name='resobin-sync',#will need to decide
    # ),
    # path(
    #     "calendar/resobin/status/",ResobinsyncronizerView.as_view(),name='resobin-status',#will need to decide
    # ),
     path(
        "calendar/feed/",FeedView.as_view(),name='feed',
    ),
     path(
        "calendar/shared/",sharedCalendarInfoView.as_view(),name='shared-calendar',
    ),
    path(
        "calendar/shared/<slug:slug>/",sharedCalendarInfoView.as_view(),name='shared-calendar-info',
    ),
    path(
        "calendar/shared/<slug:slug>/events/",sharedCalendarInfoView.as_view(),name='shared-calendar-admin',
    ),
    path(
        "calendar/shared/<slug:slug>/events/<uuid:event_id>/",sharedCalendarInfoView.as_view(),name='shared-calendar-admin-editables',
    ),
    path(
        "calendar/shared/<slug:slug>/subscribe/",UseCalendarSubscriptionView.as_view(),name='calendar-subscribe',
    ),
    path(
        "calendar/shared/<slug:slug>/unsubscribe/",UseCalendarSubscriptionView.as_view(),name='calendar-unsubscribe',
    ),
    path(
        "calendar/shared/<slug:slug>/toggle/",UseCalendarSubscriptionView.as_view(),name='calendar-toggle',
    ),
]