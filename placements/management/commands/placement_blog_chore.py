import feedparser
import requests
from requests.auth import HTTPBasicAuth
from dateutil.parser import parse
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from notifications.signals import notify
from users.models import UserProfile
from placements.models import BlogEntry

# Prefetch objects
PROFILES = UserProfile.objects.all()

def fill_blog(url):
    # Get the feed
    response = requests.get(url, auth=HTTPBasicAuth(
        settings.LDAP_USERNAME, settings.LDAP_PASSWORD))
    feeds = feedparser.parse(response.content)

    if not feeds['feed']:
        raise CommandError('PLACEMENTS BLOG CHORE FAILED')

    # Add each entry if doesn't exist
    for entry in feeds['entries']:
        # Try to get an entry existing
        guid = entry['id']
        db_entries = BlogEntry.objects.filter(guid=guid)
        new_added = False

        # Reuse if entry exists, create new otherwise
        if db_entries.exists():
            db_entry = db_entries[0]
        else:
            db_entry = BlogEntry.objects.create(guid=guid)
            db_entry.blog_url = url
            new_added = True

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

        # Send notification to mentioned people
        if new_added and db_entry.content:
            # Filter profiles
            f_profiles = (p for p in PROFILES if p.roll_no in db_entry.content)

            # Send notofications for mentioned users
            for profile in f_profiles:
                notify.send(db_entry, recipient=profile.user, verb="You were mentioned in a blog post")

class Command(BaseCommand):
    help = 'Updates the placement blog database'

    def handle(self, *args, **options):
        """Run the chore."""

        fill_blog(settings.PLACEMENTS_URL)
        fill_blog(settings.TRAINING_BLOG_URL)

        self.stdout.write(self.style.SUCCESS('Placement Blog Chore completed successfully'))
