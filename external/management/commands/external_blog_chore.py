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
    """Handle a single entry from a feed."""

    # Try to get an entry existing
    guid = entry["id"]
    db_entry = ExternalBlogEntry.objects.filter(guid=guid).first()
    # new_added = False

    # Reuse if entry exists, create new otherwise
    if not db_entry:
        db_entry = ExternalBlogEntry(guid=guid)
        new_added = True

    # Fill the db entry
    if "author" in entry:
        db_entry.body = entry["author"]
    if "title" in entry:
        db_entry.title = entry["title"]
    if "summary" in entry and entry["summary"]:
        db_entry.content = handle_html(entry["summary"])
    if "published" in entry:
        db_entry.published = parse(entry["published"])

    db_entry.save()

    # Finding the External Blog Body
    body = Body.objects.filter(name="External Blog").first()

    # Send notification to mentioned people
    if new_added and db_entry.content:
        # Send notifications to followers
        if body is not None:
            users = User.objects.filter(
                id__in=body.followers.filter(active=True).values("user_id")
            )
            notify.send(db_entry, recipient=users, verb="New post on " + body.name)

    #     # Send notifications for mentioned users
    #     roll_nos = [p for p in profile_fetcher.get_roll() if p and p in db_entry.content]
    #     if roll_nos:
    #         users = User.objects.filter(profile__roll_no__in=roll_nos)
    #         notify.send(db_entry, recipient=users, verb="You were mentioned in a blog post")


def fill_blog(url):
    # Get the feed
    response = requests.get(url, timeout=10)
    feeds = feedparser.parse(response.content)

    if not feeds["feed"]:
        raise CommandError("EXTERNAL BLOG CHORE FAILED")

    # Add each entry if doesn't exist
    for entry in feeds["entries"]:
        handle_entry(entry)


def handle_html(content):
    # Convert tables to markdown
    regex = re.compile(r"<table.*?/table>", re.DOTALL)
    content = regex.sub(convert_table_md, content)
    return content


def convert_table_md(content):
    content = table_to_markdown(content.group())
    content = "\n" + content + "\n"
    return content


class Command(BaseCommand):
    help = "Updates the external blog database"

    def handle(self, *args, **options):
        """Run the chore."""

        fill_blog(settings.EXTERNAL_BLOG_URL)
        self.stdout.write(
            self.style.SUCCESS("External Blog Chore completed successfully")
        )
