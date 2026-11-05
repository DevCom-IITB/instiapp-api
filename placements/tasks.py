import re
from django.conf import settings
from django.contrib.auth.models import User
from notifications.signals import notify

from helpers.celery import shared_task_conditional, FaultTolerantTask
from bodies.models import Body
from placements.models import BlogEntry
from users.models import UserProfile
from placements.cache import invalidate_blog_cache


class ProfileFetcher:
    """Helper to get list of roll numbers efficiently."""

    def __init__(self):
        self.roll_nos = None

    def get_roll(self):
        if not self.roll_nos:
            self.roll_nos = list(
                UserProfile.objects.filter(active=True).values_list("roll_no", flat=True)
            )
        return self.roll_nos


profile_fetcher = ProfileFetcher()


@shared_task_conditional(base=FaultTolerantTask)
def process_blog_entry_async(entry_id, body_id=None):
    """
    Background worker task to:
    1. Send notifications to followers & mentioned users.
    2. Run NLP domain classification (spaCy) and HTML extraction.
    3. Invalidate Redis cache for blogs.
    """
    # Invalidate cache so fresh data is fetched on next API call
    invalidate_blog_cache()

    db_entry = BlogEntry.objects.filter(id=entry_id).first()
    if not db_entry:
        return

    body = Body.objects.filter(id=body_id).first() if body_id else None

    # 1. NOTIFICATIONS
    if db_entry.content:
        # A. Send notifications to followers of the body (Placement / Internship)
        if body is not None:
            follower_user_ids = body.followers.filter(active=True).values_list("user_id", flat=True)
            if follower_user_ids:
                users = User.objects.filter(id__in=follower_user_ids)
                notify.send(db_entry, recipient=users, verb="New post on " + body.name)

        # B. Send notifications to mentioned roll numbers in the post content
        content_lower = db_entry.content.lower()
        words_in_post = set(re.findall(r"\b\w+\b", content_lower))
        all_rolls = profile_fetcher.get_roll()
        mentioned_rolls = [r for r in all_rolls if r and r.lower() in words_in_post]

        if mentioned_rolls:
            mentioned_users = User.objects.filter(profile__roll_no__in=mentioned_rolls)
            notify.send(
                db_entry,
                recipient=mentioned_users,
                verb="You were mentioned in a blog post",
            )

    # 2. NLP INGESTION & DATA EXTRACTION (spaCy + BeautifulSoup)
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
        print(f"[Celery] Failed to extract NLP data for blog entry {entry_id}: {e}")

