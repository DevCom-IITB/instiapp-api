"""Chore to send rich notifications for event about to start."""
from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from pyfcm import FCMNotification
from events.models import Event
from helpers.fcm import send_notification_fcm

class Command(BaseCommand):
    help = 'Sends push notifications of event starting'

    def handle(self, *args, **options):
        # Initiate connection
        push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)

        # Maintain a count
        count = 0

        # Iterate all upcoming events
        for event in Event.objects.filter(
                start_time__range=(timezone.now(), timezone.now() + timedelta(minutes=30)),
                starting_notified=False):

            # Stop the spam!
            event.starting_notified = True
            event.notify = False
            event.save()

            # Event About to Start
            print('EATS -', event.name)

            # Construct object
            data_message = {
                "type": "event",
                "id": str(event.id),
                "title": event.name,
                "verb": "Event is about to start",
                "large_icon": event.bodies.first().image_url,
                "image_url": event.image_url
            }

            # Notify all followers
            for profile in event.followers.all():
                # Send FCM push notification
                for device in profile.devices.all():
                    count += send_notification_fcm(push_service, device, data_message)

        print('Sent', count, 'rich notifications')
        self.stdout.write(self.style.SUCCESS('Event starting chore completed successfully'))
