"""Mark users who haven't pinged in a year as inactive."""
from datetime import timedelta
from django.utils.timezone import now
from django.core.management.base import BaseCommand
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Mark users inactive'

    def handle(self, *args, **options):
        queryset = UserProfile.objects.filter(last_ping__lte=now() - timedelta(days=365))
        print('Marking %s users as inactive' % queryset.count())
        queryset.update(active=False)
