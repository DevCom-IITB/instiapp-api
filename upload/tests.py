"""Unit tests for upload."""
import os
from os.path import isfile
from datetime import timedelta
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from freezegun import freeze_time
from rest_framework.test import APITestCase

from login.tests import get_new_user
from helpers.test_helpers import create_event
from helpers.test_helpers import create_body

from upload.models import UploadedImage

get_image = lambda: SimpleUploadedFile(
    "img.jpg", open("./upload/img.jpg", "rb").read(), content_type="image/jpeg")

new_upload = lambda slf: slf.client.post('/api/upload', {'picture': get_image()})

class UploadTestCase(APITestCase):
    """Check if logged in users can upload files."""

    def setUp(self):
        self.user = get_new_user()
        self.client.force_login(self.user)

    def test_upload(self):
        """Test if logged in users can upload files."""

        # Try without authentication
        self.client.logout()
        url = '/api/upload'
        data = {
            "picture": open('./upload/b64img.txt', 'r').read()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)

        # Try again with login
        self.client.force_login(self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        # Check if extension was guessed right
        img_id = response.data['id']
        img = UploadedImage.objects.get(pk=img_id)
        self.assertIn('.png', str(img.picture))

        # Check __str__
        self.assertEqual(str(img), str(img.time_of_creation))

        # Test delete
        url = '/api/upload/' + img_id
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 204)

        # Check POST file upload
        response = new_upload(self)

        # Check if the file was uploaded
        img_id = response.data['id']
        img = UploadedImage.objects.get(pk=img_id)
        self.assertIn('.jpg', str(img.picture))

    def test_clean_images_chore(self):
        """Check clean images chore."""

        res = [None] * 5
        res[0] = new_upload(self)

        # Create images more than an hour ago
        with freeze_time(timezone.now() - timedelta(hours=3)):
            for i in range(1, 5):
                res[i] = new_upload(self)

            event1 = create_event(image_url=res[2].data['picture'])
            body1 = create_body(image_url=res[3].data['picture'])

        # Get path for checking deletion
        obj = lambda res: UploadedImage.objects.get(pk=res.data['id'])
        obj_exists = lambda res: UploadedImage.objects.filter(pk=res.data['id']).exists()
        paths = [obj(r).picture.path for r in res]

        # Check if deleting a non existent file is fine
        self.assertTrue(isfile(paths[4]))
        os.remove(paths[4])
        self.assertFalse(isfile(paths[4]))
        obj(res[4]).delete()
        self.assertFalse(obj_exists(res[4]))

        # Call the chore
        clean = lambda: call_command('clean-images')
        clean()

        # Check if unclaimed images were removed
        self.assertTrue(obj_exists(res[0]))
        self.assertFalse(obj_exists(res[1]))
        self.assertTrue(obj_exists(res[2]))
        self.assertTrue(obj_exists(res[3]))

        # Check if file is deleted
        self.assertTrue(isfile(paths[0]))
        self.assertFalse(isfile(paths[1]))

        # Check after invalidating claimant
        body1.image_url = 'https://insti.app'
        body1.save()
        clean()
        self.assertTrue(obj_exists(res[2]))
        self.assertFalse(obj_exists(res[3]))

        # Check after deleting claimant
        event1.delete()
        clean()
        self.assertFalse(obj_exists(res[2]))
