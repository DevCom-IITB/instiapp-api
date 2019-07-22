"""Views for prerendered content for SEO."""
from uuid import UUID
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from users.models import UserProfile
from events.models import Event
from events.prioritizer import get_fresh_prioritized_events
from news.models import NewsEntry
from bodies.models import Body
from locations.models import Location

url_mapping = {
    Event: '/event/',
    Body: '/org/'
}

class Crumb:  # pylint: disable=R0903
    def __init__(self, obj, index):
        has_canonical = hasattr(obj, 'canonical_name') and obj.canonical_name
        self.name = obj.canonical_name if has_canonical else obj.name
        self.url = settings.BASE_URL + url_mapping[obj.__class__] + obj.str_id
        self.index = index

def get_body_breadcrumb(body):
    """Gets a trail of breadcrumb from a body."""
    trails = []
    for parent in body.parents.all():
        big_bread = get_body_breadcrumb(parent.parent)
        for bread in big_bread:
            bread.append(Crumb(body, bread[-1].index + 1))
            trails.append(bread)
        if not big_bread:
            trails.append([Crumb(body, 1)])
    return trails

def get_event_breadcrumb(event):
    """Gets a trail of breadcrumb from an event."""
    trails = []
    for body in event.bodies.all():
        for bread in get_body_breadcrumb(body):
            bread.append(Crumb(event, bread[-1].index + 1))
            trails.append(bread)
    return trails

def root(request):
    events = get_fresh_prioritized_events(Event.objects.all(), request)
    rendered = render_to_string('root.html', {'events': events, 'settings': settings})
    return HttpResponse(rendered)

def news(request):
    news_items = NewsEntry.objects.all()[0:20]
    news_items = news_items.prefetch_related('body')
    rendered = render_to_string('news.html', {'news': news_items, 'settings': settings})
    return HttpResponse(rendered)

def explore(request):
    bodies = Body.objects.all()
    rendered = render_to_string('explore.html', {'bodies': bodies, 'settings': settings})
    return HttpResponse(rendered)

def user_details(request, pk):
    queryset = UserProfile.objects.prefetch_related('roles', 'roles__body')
    try:
        UUID(pk, version=4)
        profile = get_object_or_404(queryset, pk=pk)
    except ValueError:
        profile = get_object_or_404(queryset, ldap_id=pk)

    if profile.profile_pic is None:
        profile.profile_pic = settings.USER_AVATAR_URL

    rendered = render_to_string('user-details.html', {
        'profile': profile,
        'achievements': profile.achievements.prefetch_related('body', 'event').filter(hidden=False),
        'settings': settings
    })
    return HttpResponse(rendered)

def event_details(request, pk):
    # Prefetch
    queryset = Event.objects.prefetch_related('bodies', 'venues')

    try:
        UUID(pk, version=4)
        event = get_object_or_404(queryset, pk=pk)
    except ValueError:
        event = get_object_or_404(queryset, str_id=pk)

    rendered = render_to_string('event-details.html', {
        'event': event,
        'settings': settings,
        'bread': get_event_breadcrumb(event),
    })
    return HttpResponse(rendered)

def body_details(request, pk):
    # Get queryset
    queryset = Body.objects

    try:
        UUID(pk, version=4)
        body = get_object_or_404(queryset, pk=pk)
    except ValueError:
        body = get_object_or_404(queryset, str_id=pk)

    events = get_fresh_prioritized_events(body.events, request, delta=365)

    rendered = render_to_string('body-details.html', {
        'body': body,
        'settings': settings,
        'events': events,
        'bread': get_body_breadcrumb(body),
    })
    return HttpResponse(rendered)

def body_tree(request, pk):
    body = get_object_or_404(Body.objects, pk=pk)

    rendered = render_to_string('body-tree.html', {
        'body': body,
        'settings': settings,
    })
    return HttpResponse(rendered)

def insti_map(request, name=None):
    """Prerender for map thumbnails."""

    # Filter with str_id
    location = Location.objects.filter(reusable=True, str_id=name).first()

    # Create dummy if we found nothing
    if not location:
        location = Location()
        location.id = 'default'
        location.name = "place"
        location.str_id = None
        location.short_name = "Map"

    # (Ugly) Add slash to start of str id to display in URL
    location.str_id = ('/%s' % location.str_id) if location.str_id else ''

    # Render the response
    rendered = render_to_string('map.html', {
        'loc': location,
        'image_url': '%s%smap/%s.jpg' % (settings.STATIC_BASE_URL, settings.STATIC_URL, location.id),
        'settings': settings,
    })

    return HttpResponse(rendered)

def mstile(request):
    """Prerender for UWP live tiles"""
    images = Event.objects.filter(
        end_time__gte=timezone.now()).order_by('start_time').values_list('image_url', flat=True)

    rendered = render_to_string('ms-tile.xml', {
        'images': [x for x in images[:10] if x],
        'tilenames': ['TileMedium', 'TileWide', 'TileLarge'],
        'settings': settings,
    })
    return HttpResponse(rendered, content_type='text/xml')
