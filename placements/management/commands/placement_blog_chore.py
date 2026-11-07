import pickle
import re
from os.path import exists
from requests.auth import HTTPBasicAuth
import feedparser
import requests
from dateutil.parser import parse
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from notifications.signals import notify
from users.models import UserProfile
from bodies.models import Body
from placements.models import BlogEntry
from helpers.misc import table_to_markdown
from placements.cache import invalidate_blog_cache


class ProfileFetcher:
    """Helper to get list of active user roll numbers efficiently."""

    def __init__(self):
        self.roll_nos = None

    def get_roll(self):
        if not self.roll_nos:
            self.roll_nos = UserProfile.objects.filter(active=True).values_list(
                "roll_no", flat=True
            )
        return self.roll_nos


profile_fetcher = ProfileFetcher()


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

    # Invalidate blog cache when a new entry is added.
    if new_added:
        invalidate_blog_cache()

    # Send notifications to followers and mentioned users for new entries.
    if new_added and db_entry.content:
        if body is not None:
            users = User.objects.filter(
                id__in=body.followers.filter(active=True).values("user_id")
            )
            notify.send(db_entry, recipient=users, verb="New post on " + body.name)

        content_lower = db_entry.content.lower()
        words_in_post = set(re.findall(r"\b\w+\b", content_lower))
        roll_nos = [
            roll_no
            for roll_no in profile_fetcher.get_roll()
            if roll_no and roll_no.lower() in words_in_post
        ]
        if roll_nos:
            users = User.objects.filter(profile__roll_no__in=roll_nos)
            notify.send(
                db_entry,
                recipient=users,
                verb="You were mentioned in a blog post",
            )

    # Keep NLP ingestion in the chore process, as before Celery offloading.
    try:
        feed_post_format = [{
            "id": str(db_entry.id),
            "title": db_entry.title,
            "content": db_entry.content,
            "link": db_entry.link,
            "published": db_entry.published.isoformat() if db_entry.published else None,
        }]

        if body and body.name == getattr(settings, "PLACEMENTS_BLOG_BODY", ""):
            from placementblogs.data_extractor import run_production_ingestion
            run_production_ingestion(feed_post_format)
        elif body and body.name == getattr(settings, "TRAINING_BLOG_BODY", ""):
            from internship.data_extractor import run_production_ingestion
            run_production_ingestion(feed_post_format)
    except Exception as e:
        print(f"Failed to extract NLP data for blog entry {db_entry.id}: {e}")


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
