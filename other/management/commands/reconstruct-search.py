"""Reconstruct all search indices."""
from datetime import timedelta
from asonic import Client as SonicClient
from asonic.enums import Channel as SonicChannel
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from other.search import push, index_pair, consolidate
from other.asyncio_run import run_sync

from bodies.models import Body
from events.models import Event
from events.prioritizer import get_fresh_events
from users.models import UserProfile
from placements.models import BlogEntry
from news.models import NewsEntry

async def refresh(queryset):
    # Get client
    client = SonicClient(**settings.SONIC_CONFIG)
    await client.channel(SonicChannel.INGEST)

    # Index all objects
    for i, obj in enumerate(queryset):
        pair = index_pair(obj)

        # Flush on first object
        if i == 0:
            await client.flushc(pair[0])

        # Push object
        await push(pair, client=client)

class Command(BaseCommand):
    help = 'Reconstruct all search indices'

    def handle(self, *args, **options):
        if not settings.USE_SONIC:
            return

        # Refresh all bodies and news
        run_sync(refresh(Body.objects.all()))
        run_sync(refresh(NewsEntry.objects.all()))

        # Refresh events younger than two years
        run_sync(refresh(get_fresh_events(Event.objects, delta=600)))

        # Refresh entries younger than two years
        placement = BlogEntry.objects.filter(
            published__gte=timezone.now() - timedelta(days=600))
        run_sync(refresh(placement))

        # Refresh active users
        run_sync(refresh(UserProfile.objects.filter(active=True)))

        # Re-consolidate
        run_sync(consolidate())
