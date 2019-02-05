"""Chore to generate map location thumbnails."""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image
from locations.models import Location

MAP_FILE = 'map.jpg'
MARKER_FILE = 'marker.png'
PIXEL_SPAN_H = 500
PIXEL_SPAN_V = 400
MARKER_SIZE = 54, 54
SAVE_FOLDER = '%s/map' % (settings.STATIC_ROOT)

# pylint: disable=R0914
class Command(BaseCommand):
    help = 'Generate thumbnails for all reusable locations'

    def handle(self, *args, **options):
        # Provide this the map file in the working directory
        image = Image.open(open(MAP_FILE, 'rb'))
        marker = Image.open(open(MARKER_FILE, 'rb'))
        marker.thumbnail(MARKER_SIZE, Image.ANTIALIAS)
        marker_width, marker_height = marker.size

        # Check for target directory
        if not os.path.exists(SAVE_FOLDER):
            os.makedirs(SAVE_FOLDER)

        # Iterate all locations
        for location in Location.objects.filter(reusable=True):
            # Check for invalid locations
            if not location.pixel_x or not location.pixel_y:
                continue

            # Check for dummy locations:
            if location.pixel_x <= 0 or location.pixel_y <= 0:
                continue

            # Account for bias due to marker
            v_bias = marker_height // 4

            # Crop the iamge
            left = location.pixel_x - PIXEL_SPAN_H // 2
            top = location.pixel_y - PIXEL_SPAN_V // 2 - v_bias
            right = location.pixel_x + PIXEL_SPAN_H // 2
            bottom = location.pixel_y + PIXEL_SPAN_V // 2 - v_bias
            cropped = image.crop((left, top, right, bottom))

            # Add marker
            marker_x = (PIXEL_SPAN_H - marker_width) // 2
            marker_y = (PIXEL_SPAN_V // 2) - marker_height + v_bias
            cropped.paste(marker, (marker_x, marker_y), marker)

            # Save the image
            save_path = '%s/%s.jpg' % (SAVE_FOLDER, location.id)
            cropped.save(save_path, 'JPEG', quality=90, optimize=True, progressive=True)

            # Print a message
            print('Created image for', location.short_name)
