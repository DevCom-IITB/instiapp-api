import os
from glob import glob
from django.core.management.base import BaseCommand
from django.conf import settings
from upload.models import UploadedImage

# Other reserved files
reserved = [
    'useravatar.jpg'
]

def is_reserved(file):
    return any(r in file for r in reserved)

class Command(BaseCommand):
    help = 'Clean static directory.'

    def handle(self, *args, **options):
        """Clean static directory."""

        verified = 0
        cleaned = 0

        # List of all valid images
        images = [x.picture.path for x in UploadedImage.objects.all()]

        # List of all files recursive
        files = [y for x in os.walk(settings.MEDIA_ROOT) for y in glob(os.path.join(x[0], '*'))]
        for file in files:
            if not os.path.isfile(file):
                continue

            # Check if the file is valid
            if os.path.abspath(file) in images or is_reserved(file):
                verified += 1
                print('Verified', file)
            else:
                cleaned += 1
                print('Cleaned', file)
                os.remove(os.path.abspath(file))

        self.stdout.write(self.style.SUCCESS('%i uploaded image files verified, %i cleaned' % (verified, cleaned)))
