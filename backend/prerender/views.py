"""Views for prerendered content for SEO."""
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.conf import settings
from users.models import UserProfile
from events.models import Event

def user_details(request, pk):
    profile = get_object_or_404(UserProfile.objects, pk=pk)
    if profile.profile_pic is None:
        profile.profile_pic = settings.USER_AVATAR_URL

    rendered = render_to_string('user-details.html', {'profile': profile, 'settings': settings})
    return HttpResponse(rendered)

def event_details(request, pk):
    event = get_object_or_404(Event.objects, pk=pk)
    rendered = render_to_string('event-details.html', {'event': event, 'settings': settings})
    return HttpResponse(rendered)
