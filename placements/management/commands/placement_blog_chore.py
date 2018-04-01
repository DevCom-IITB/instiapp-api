import feedparser
import requests
from requests.auth import HTTPBasicAuth
from dateutil.parser import parse
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from placements.models import PlacementBlogEntry

class Command(BaseCommand):
    help = 'Updates the placement blog database'

    def handle(self, *args, **options):
        """Run the chore."""

        url = settings.PLACEMENTS_URL
        response = requests.get(url, auth=HTTPBasicAuth(
            settings.LDAP_USERNAME, settings.LDAP_PASSWORD))
        feeds = feedparser.parse(response.content)

        if not feeds['feed']:
            raise CommandError('PLACEMENTS BLOG CHORE FAILED')

        for entry in feeds['entries']:
            # Try to get an entry existing
            guid = entry['id']
            db_entries = PlacementBlogEntry.objects.filter(guid=guid)

            # Reuse if entry exists, create new otherwise
            if db_entries.exists():
                db_entry = db_entries[0]
            else:
                db_entry = PlacementBlogEntry.objects.create(guid=guid)

            # Fill the db entry
            if 'title' in entry:
                db_entry.title = entry['title']
            if 'content' in entry and entry['content']:
                db_entry.content = entry['content'][0]['value']
            if 'link' in entry:
                db_entry.link = entry['link']
            if 'published' in entry:
                db_entry.published = parse(entry['published'])

            db_entry.save()

        self.stdout.write(self.style.SUCCESS('Placement Blog Chore completed successfully'))
