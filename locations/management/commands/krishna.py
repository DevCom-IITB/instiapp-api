import re
import feedparser
import requests
from notifications.signals import notify
from dateutil.parser import parse
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from external.models import ExternalBlogEntry
from bodies.models import Body
from helpers.misc import table_to_markdown

from locations.models import Location, LocationLocationDistance


# class ProfileFetcher():
#     """Helper to get dictionary of profiles efficiently."""
#     def __init__(self):
#         self.roll_nos = None

#     def get_roll(self):
#         if not self.roll_nos:
#             self.roll_nos = UserProfile.objects.filter(active=True).values_list('roll_no', flat=True)
#         return self.roll_nos


# profile_fetcher = ProfileFetcher()

def handle_entry(entry):
    coordinates = [(4228, 943), (4005, 899), (2100, 756)]
    adj_list = {
        0: {1: -1, 2: -1},
        1: {0: -1},
        2: {0: -1},
    }
    for x in adj_list:
        for y in adj_list[x]:
            adj_list[x][y] = abs(0.001 * ((coordinates[x][0] ^ 2) - (coordinates[y][0] ^ 2) +
                                 (coordinates[x][1] ^ 2) - (coordinates[y][1] ^ 2)))

    i = 0
    loc_list = []
    for p in coordinates:
        loc, c = Location.objects.get_or_create(pixel_x=p[0], pixel_y=p[1], name="Node" + str(i))
        loc_list.append(loc)
        i += 1

    for i in range(0, len(coordinates)):
        loc1 = loc_list[i]
        print(adj_list[i])
        for loc2_ind in adj_list[i]:
            loc2 = loc_list[loc2_ind]
            dist = adj_list[i][loc2_ind]
            lld = LocationLocationDistance.objects.filter(location1__id=loc1.id, location2__id=loc2.id).first()
            if not lld:
                LocationLocationDistance.objects.create(
                    location1=loc1, location2=loc2, distance=dist)
            else:
                lld.distance = dist
                lld.save()


class Command(BaseCommand):
    help = 'Updates the external blog database'

    def handle(self, *args, **options):
        """Run the chore."""

        handle_entry(settings.EXTERNAL_BLOG_URL)
        self.stdout.write(self.style.SUCCESS('External Blog Chore completed successfully'))
