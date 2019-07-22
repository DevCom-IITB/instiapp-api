"""Reconstruct all search indices."""
import asyncio
from django.core.management.base import BaseCommand
from other.search import index_pair, push, consolidate

from bodies.models import Body
from events.models import Event
from users.models import UserProfile
from placements.models import BlogEntry
from news.models import NewsEntry

class Command(BaseCommand):
    help = 'Reconstruct all search indices'

    def handle(self, *args, **options):
        for model in (Body, Event, UserProfile, BlogEntry, NewsEntry):
            # Get all pairs to be indexed
            pairs = [index_pair(v) for v in model.objects.all()]

            # Push all pairs
            asyncio.run(push(pairs))

        # Re-consolidate
        asyncio.run(consolidate())
