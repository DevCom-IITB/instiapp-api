"""Chore to aggregate news from all bodies."""
from datetime import timedelta
import feedparser
import requests
import urllib3
from dateutil.parser import parse
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from news.models import NewsEntry
from bodies.models import Body

# Disable log garbage due to Insecure warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fill_blog(url, body):
    response = requests.get(url, verify=False)
    feeds = feedparser.parse(response.content)

    if not feeds['feed']:
        raise CommandError('NEWS CHORE FAILED')

    # Log number of new entries
    existing_entries = 0
    new_entries = 0
    min_pub = timezone.now() - timedelta(days=2)

    for entry in feeds['entries']:
        # Try to get an entry existing
        guid = entry['id']
        db_entries = NewsEntry.objects.filter(guid=guid)
        is_new_entry = not db_entries.exists()

        # Reuse if entry exists, create new otherwise
        if not is_new_entry:
            db_entry = db_entries[0]
            existing_entries += 1
        else:
            db_entry = NewsEntry(guid=guid, body=body)
            db_entry.blog_url = url
            new_entries += 1

        # Fill the db entry
        if 'title' in entry:
            db_entry.title = entry['title']
        if 'description' in entry:
            db_entry.content = entry['description']
        if 'link' in entry:
            db_entry.link = entry['link']
        if 'content' in entry and db_entry.content == "":
            # Fill in content only if we don't have description
            db_entry.content = entry['content'][0]['value']

        # Disable notifications if published long ago or unknown
        has_published = 'published' in entry
        if has_published:
            db_entry.published = parse(entry['published'])

        # Check if news article is old and for too many articles
        if is_new_entry and not has_published or new_entries > 3 or min_pub > db_entry.published:
            db_entry.notify = False

        db_entry.save()

    print("(+" + str(new_entries) + ", " + str(existing_entries) + ") ", end="")

class Command(BaseCommand):
    help = 'Updates the placement blog database'

    def handle(self, *args, **options):
        """Run the chore."""

        for body in Body.objects.all():
            if body.blog_url is None or body.blog_url == "":
                continue

            try:
                print("Aggregating for", body.name, "- ", end="", flush=True)
                fill_blog(body.blog_url, body)
                print("")
            except Exception:  # pylint: disable=W0703
                print("Failed!")

        self.stdout.write(self.style.SUCCESS('News Chore completed successfully'))
