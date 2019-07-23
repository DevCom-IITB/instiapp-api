"""Reconstruct all search indices."""
from asonic import Client as SonicClient
from asonic.enums import Channels as SonicChannels
from django.conf import settings
from django.core.management.base import BaseCommand
from other.search import push, index_pair, consolidate
from other.asyncio_run import run_sync

from bodies.models import Body
from events.models import Event
from users.models import UserProfile
from placements.models import BlogEntry
from news.models import NewsEntry

async def refresh(queryset):
    # Get client
    client = SonicClient(**settings.SONIC_CONFIG)
    await client.channel(SonicChannels.INGEST.value)

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

        for model in (Body, Event, UserProfile, BlogEntry, NewsEntry):
            # Refresh all objects
            run_sync(refresh(model.objects.all()))

        # Re-consolidate
        run_sync(consolidate())
