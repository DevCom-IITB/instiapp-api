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

async def refresh():
    # Get client
    client = SonicClient(**settings.SONIC_CONFIG)
    await client.channel(SonicChannels.INGEST.value)

    # Index all objects
    for model in (Body, Event, UserProfile, BlogEntry, NewsEntry):
        for obj in model.objects.all():
            await push(index_pair(obj), client=client)

class Command(BaseCommand):
    help = 'Reconstruct all search indices'

    def handle(self, *args, **options):
        if not settings.USE_SONIC:
            return

        # Refresh all objects
        run_sync(refresh())

        # Re-consolidate
        run_sync(consolidate())
