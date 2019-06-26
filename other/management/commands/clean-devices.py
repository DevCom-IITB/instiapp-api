"""Clean up old devices that haven't pinged since a long time."""
from datetime import timedelta
from django.utils.timezone import now
from django.core.management.base import BaseCommand
from other.models import Device

class Command(BaseCommand):
    help = 'Clean up old devices'

    def handle(self, *args, **options):
        queryset = Device.objects.filter(last_ping__lte=now() - timedelta(days=90))
        print('Cleaning up %s old devices' % queryset.count())
        queryset.delete()
