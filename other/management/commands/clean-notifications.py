"""Clean up old notifications (older than 3 months)"""
from datetime import timedelta
import json

from django.utils.timezone import now
from django.core.management.base import BaseCommand
from notifications.models import Notification

class Command(BaseCommand):
    help = 'Clean up old notifications (older than 3 months)'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Give directory path for dumping old notifs without end slash')

    def handle(self, *args, **options):
        file_path = options['path'] + '/' + str(now().date()) + '.txt'
        queryset = Notification.objects.filter(timestamp__lte=now() - timedelta(days=90))
        print('Dumping and Cleaning up %s old notifications' % queryset.count())
        if queryset.count() > 0:
            data = list(queryset.values())
            with open(file_path) as f:
                json.dump(data, f, ensure_ascii=False, default=str)
            queryset.delete()
