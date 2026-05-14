"""Refresh all devices with info from FCM."""
from django.conf import settings
from django.core.management.base import BaseCommand
from other.models import Device


class Command(BaseCommand):
    help = "Refresh all devices (deprecated - Firebase Admin doesn't require manual refresh)"

    def handle(self, *args, **options):
        # Firebase Admin SDK handles device validation automatically
        # This command is no longer needed but kept for backwards compatibility
        print("Device refresh is now handled automatically by Firebase Admin SDK")
        print("Invalid tokens will be detected on send attempts and removed as needed")
