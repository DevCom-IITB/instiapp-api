from django.contrib.sitemaps import Sitemap
from events.models import Event
from events.prioritizer import get_fresh_events
from bodies.models import Body

class EventSitemap(Sitemap):
    changefreq = "never"
    priority = 0.7

    def items(self):
        return get_fresh_events(Event.objects.all(), 365)

    def lastmod(self, obj):
        return obj.time_of_modification

class BodySitemap(Sitemap):
    changefreq = "never"
    priority = 0.6

    def items(self):
        return Body.objects.all()

    def lastmod(self, obj):
        return obj.time_of_modification

class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return ['/', '/news', '/explore']

    def location(self, item):
        return item

def sitemaps():
    return {
        'event': EventSitemap,
        'body': BodySitemap,
        'static': StaticViewSitemap,
    }
