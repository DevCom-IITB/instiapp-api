import re
import feedparser
import requests
from requests.auth import HTTPBasicAuth
from dateutil.parser import parse
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from notifications.signals import notify
from users.models import UserProfile
from bodies.models import Body
from placements.models import BlogEntry
from helpers.misc import table_to_markdown

class ProfileFetcher():
    """Helper to get dictionary of profiles efficiently."""
    def __init__(self):
        self.profiles = None

    def get(self):
        if not self.profiles:
            self.profiles = UserProfile.objects.values('roll_no')
        return self.profiles


profile_fetcher = ProfileFetcher()

def handle_entry(entry, body, url):
    """Handle a single entry from a feed."""

    # Try to get an entry existing
    guid = entry['id']
    db_entries = BlogEntry.objects.filter(guid=guid)
    new_added = False

    # Reuse if entry exists, create new otherwise
    if db_entries.exists():
        db_entry = db_entries[0]
    else:
        db_entry = BlogEntry(guid=guid, blog_url=url)
        new_added = True

    # Fill the db entry
    if 'title' in entry:
        db_entry.title = entry['title']
    if 'content' in entry and entry['content']:
        db_entry.content = handle_html(entry['content'][0]['value'])
    if 'link' in entry:
        db_entry.link = entry['link']
    if 'published' in entry:
        db_entry.published = parse(entry['published'])

    db_entry.save()

    # Send notification to mentioned people
    if new_added and db_entry.content:
        # Send notifications to followers
        if body is not None:
            users = User.objects.filter(id__in=body.followers.values('user__id'))
            notify.send(db_entry, recipient=users, verb="New post on " + body.name)

        # Send notifications for mentioned users
        profiles = [p for p in profile_fetcher.get() if p['roll_no'] and p['roll_no'] in db_entry.content]
        for profile in profiles:
            try:
                user = User.objects.get(profile__roll_no=profile['roll_no'])
                notify.send(db_entry, recipient=user, verb="You were mentioned in a blog post")
            except User.DoesNotExist:
                pass

def fill_blog(url, body_name):
    # Get the body
    body = None
    bodies = Body.objects.filter(name=body_name)
    if bodies.exists():
        body = bodies.first()

    # Get the feed
    response = requests.get(url, auth=HTTPBasicAuth(
        settings.LDAP_USERNAME, settings.LDAP_PASSWORD))
    feeds = feedparser.parse(response.content)

    if not feeds['feed']:
        raise CommandError('PLACEMENTS BLOG CHORE FAILED')

    # Add each entry if doesn't exist
    for entry in feeds['entries']:
        handle_entry(entry, body, url)

def handle_html(content):
    # Convert tables to markdown
    regex = re.compile(r"<table.*?/table>", re.DOTALL)
    content = regex.sub(convert_table_md, content)
    return content

def convert_table_md(content):
    content = table_to_markdown(content.group())
    content = '\n' + content + '\n'
    return content

class Command(BaseCommand):
    help = 'Updates the placement blog database'

    def handle(self, *args, **options):
        """Run the chore."""

        fill_blog(settings.PLACEMENTS_URL, settings.PLACEMENTS_BLOG_BODY)
        fill_blog(settings.TRAINING_BLOG_URL, settings.TRAINING_BLOG_BODY)

        self.stdout.write(self.style.SUCCESS('Placement Blog Chore completed successfully'))
