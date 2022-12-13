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
    coordinates = [(4228,943),(4005,899),(2100,756)]
    adj_list = {
    0: {1:-1, 2:-1},
    1: {0:-1},
    2: {0:-1},
    }
    for x in adj_list:
        for y in adj_list[x]:
             adj_list[x][y] = abs(0.001*((coordinates[x][0]^2) - (coordinates[y][0]^2) + (coordinates[x][1]^2) - (coordinates[y][1]^2)))
       



class Command(BaseCommand):
    help = 'Updates the external blog database'

    def handle(self, *args, **options):
        """Run the chore."""

        handle_entry(settings.EXTERNAL_BLOG_URL)
        self.stdout.write(self.style.SUCCESS('External Blog Chore completed successfully'))        
    