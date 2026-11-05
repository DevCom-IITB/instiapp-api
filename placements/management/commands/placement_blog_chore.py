import pickle
import re
from os.path import exists
from requests.auth import HTTPBasicAuth
import feedparser
import requests
from dateutil.parser import parse
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from bodies.models import Body
from placements.models import BlogEntry
from helpers.misc import table_to_markdown
from placements.cache import invalidate_blog_cache


def handle_entry(entry, body, url):
    """Handle a single entry from a feed."""

    # Try to get an entry existing
    guid = entry["id"]
    title = entry.get("title", "")
    db_entry = BlogEntry.objects.filter(guid=guid, title=title).first()
    new_added = False

    # Reuse if entry exists, create new otherwise
    if not db_entry:
        db_entry = BlogEntry(guid=guid, blog_url=url)
        new_added = True

    # Fill the db entry
    if "title" in entry:
        db_entry.title = entry["title"]
    if "content" in entry and entry["content"]:
        db_entry.content = handle_html(entry["content"][0]["value"])
    if "link" in entry:
        db_entry.link = entry["link"]
    if "published" in entry:
        db_entry.published = parse(entry["published"])

    db_entry.save()

    # Offload notifications, heavy NLP extraction, and cache invalidation to Celery
    if new_added:
        invalidate_blog_cache()
        try:
            from placements.tasks import process_blog_entry_async
            process_blog_entry_async.delay(str(db_entry.id), body.id if body else None)
        except Exception as e:
            print(f"Failed to dispatch Celery task for blog entry {db_entry.id}: {e}")


def fill_blog(url, body_name, url_val):
    # Get the body
    body = Body.objects.filter(name=body_name).first()

    if exists("session.obj"):
        with open("session.obj", "rb") as f:
            s = pickle.load(f)

        response = s.get(url, verify=False, timeout=10)
        feeds = feedparser.parse(response.content)

        if not feeds.get("feed"):
            raise CommandError(f"PLACEMENTS BLOG CHORE FAILED for {body_name}: Empty or invalid feed")

        # Add each entry if doesn't exist
        for entry in feeds.get("entries", []):
            handle_entry(entry, body, url_val)

    else:
        # Get the feed via basic auth fallback
        response = requests.get(
            url,
            auth=HTTPBasicAuth(settings.LDAP_USERNAME, settings.LDAP_PASSWORD),
            timeout=10,
        )
        feeds = feedparser.parse(response.content)

        if not feeds.get("feed"):
            raise CommandError(f"PLACEMENTS BLOG CHORE FAILED for {body_name}: Empty or invalid feed")

        # Add each entry with url_val so queries in views.py match
        for entry in feeds.get("entries", []):
            handle_entry(entry, body, url_val)


def handle_html(content):
    # Convert tables to markdown
    figregex = re.compile(
        r"<figure class=\"wp-block-table\"><table.*?/table></figure>", re.DOTALL
    )
    content = figregex.sub(convert_table_md, content)
    regex = re.compile(r"<table.*?/table>", re.DOTALL)
    content = regex.sub(convert_table_md, content)
    return content


def convert_table_md(content):
    content = table_to_markdown(content.group())
    content = "\n" + content + "\n"
    return content


class Command(BaseCommand):
    help = "Updates the placement blog database"

    def handle(self, *args, **options):
        """Run the chore with fault isolation between Placement and Internship."""
        has_error = False

        # 1. Scrape Placement Blog
        try:
            fill_blog(
                settings.PLACEMENTS_URL,
                settings.PLACEMENTS_BLOG_BODY,
                settings.PLACEMENTS_URL_VAL,
            )
            self.stdout.write(self.style.SUCCESS("Placement blog scrape completed."))
        except Exception as e:
            has_error = True
            self.stderr.write(self.style.ERROR(f"Placement blog scrape error: {e}"))

        # 2. Scrape Internship Blog (isolated: runs even if Placement failed)
        try:
            fill_blog(
                settings.TRAINING_BLOG_URL,
                settings.TRAINING_BLOG_BODY,
                settings.TRAINING_BLOG_URL_VAL,
            )
            self.stdout.write(self.style.SUCCESS("Internship blog scrape completed."))
        except Exception as e:
            has_error = True
            self.stderr.write(self.style.ERROR(f"Internship blog scrape error: {e}"))

        if has_error:
            self.stderr.write(self.style.WARNING("Placement Blog Chore completed with errors."))
        else:
            self.stdout.write(self.style.SUCCESS("Placement Blog Chore completed successfully."))
