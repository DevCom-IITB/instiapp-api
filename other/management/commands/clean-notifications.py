"""Clean up old notifications (older than 3 months)"""
from datetime import timedelta
import json

from django.utils.timezone import now
from django.core.management.base import BaseCommand
from notifications.models import Notification


class Command(BaseCommand):
    help = "Clean up old notifications (older than 3 months)"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="File path for dumping old notifs")

    def handle(self, *args, **options):
        file_path = options["file"]
        queryset = Notification.objects.filter(
            timestamp__lte=now() - timedelta(days=90)
        )
        print("Dumping and Cleaning up %s old notifications" % queryset.count())
        if queryset.count() > 0:
            notif_list = queryset.values()
            with open(file_path, "a") as f:
                for notif in notif_list:
                    json.dump(notif, f, ensure_ascii=False, default=str)
                    print("", file=f, end="\n")
            queryset.delete()
