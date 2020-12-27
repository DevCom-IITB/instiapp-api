"""Clean up old notifications (older than 3 months)"""
from datetime import timedelta
from django.utils.timezone import now
from django.core.management.base import BaseCommand
from notifications.models import Notification

class Command(BaseCommand):
    help = 'Clean up old notifications'

    def handle(self, *args, **options):
        queryset = Notification.objects.filter(timestamp__lte=now() - timedelta(days=90))
        print('Cleaning up %s old notifications' % queryset.count())
        queryset.delete()
