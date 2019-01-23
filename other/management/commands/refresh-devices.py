"""Refresh all devices with info from FCM."""
from django.conf import settings
from django.core.management.base import BaseCommand
from pyfcm import FCMNotification
from other.models import Device
from helpers.device import fill_device_firebase

class Command(BaseCommand):
    help = 'Sends push notifications of event starting'

    def handle(self, *args, **options):
        # Initiate connection
        push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)

        # Refresh all
        for device in Device.objects.all():
            print(device.user.name + ' - ', end='', flush=True)
            if fill_device_firebase(push_service, device):
                print('OK')
            else:
                device.delete()
                print('FAIL')
