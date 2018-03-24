"""Views for prerendered content for SEO."""
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.conf import settings
from users.models import UserProfile

def user_details(request, pk):
    profile = get_object_or_404(UserProfile.objects, pk=pk)
    if profile.profile_pic is None:
        profile.profile_pic = settings.USER_AVATAR_URL

    rendered = render_to_string('user-details.html', {'profile': profile, 'settings': settings})
    return HttpResponse(rendered)
