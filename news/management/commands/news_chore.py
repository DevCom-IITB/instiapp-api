"""Chore to aggregate news from all bodies."""
import feedparser
import requests
from dateutil.parser import parse
from django.core.management.base import BaseCommand, CommandError
from news.models import NewsEntry
from bodies.models import Body

def fill_blog(url, body):
    response = requests.get(url)
    feeds = feedparser.parse(response.content)

    if not feeds['feed']:
        raise CommandError('NEWS CHORE FAILED')

    # Log number of new entries
    existing_entries = 0
    new_entries = 0

    for entry in feeds['entries']:
        # Try to get an entry existing
        guid = entry['id']
        db_entries = NewsEntry.objects.filter(guid=guid)

        # Reuse if entry exists, create new otherwise
        if db_entries.exists():
            db_entry = db_entries[0]
            existing_entries += 1
        else:
            db_entry = NewsEntry.objects.create(guid=guid, body=body)
            db_entry.blog_url = url
            new_entries += 1

        # Fill the db entry
        if 'title' in entry:
            db_entry.title = entry['title']
        if 'description' in entry:
            db_entry.content = entry['description']
        if 'link' in entry:
            db_entry.link = entry['link']
        if 'published' in entry:
            db_entry.published = parse(entry['published'])
        if 'content' in entry and db_entry.content == "":
            # Fill in content only if we don't have description
            db_entry.content = entry['content'][0]['value']

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
            except Exception:
                print("Failed!")

        self.stdout.write(self.style.SUCCESS('News Chore completed successfully'))
