"""Chore to aggregate news from all bodies."""
import feedparser
import requests
from dateutil.parser import parse
from django.core.management.base import BaseCommand, CommandError
from news.models import NewsEntry, NewsSource

def fill_blog(url, body):
    response = requests.get(url)
    feeds = feedparser.parse(response.content)

    if not feeds['feed']:
        raise CommandError('NEWS CHORE FAILED')

    for entry in feeds['entries']:
        # Try to get an entry existing
        guid = entry['id']
        db_entries = NewsEntry.objects.filter(guid=guid)

        # Reuse if entry exists, create new otherwise
        if db_entries.exists():
            db_entry = db_entries[0]
        else:
            db_entry = NewsEntry.objects.create(guid=guid, body=body)
            db_entry.blog_url = url

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

class Command(BaseCommand):
    help = 'Updates the placement blog database'

    def handle(self, *args, **options):
        """Run the chore."""

        for source in NewsSource.objects.all():
            fill_blog(source.blog_url, source.body)

        self.stdout.write(self.style.SUCCESS('News Chore completed successfully'))
