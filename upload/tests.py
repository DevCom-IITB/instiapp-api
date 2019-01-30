"""Unit tests for upload."""
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

class UploadTestCase(APITestCase):
    """Check if logged in users can upload files."""

    def test_upload(self):  # pylint: disable=R0914
        """Test if logged in users can upload files."""

        # Try without authentication
        url = '/api/upload'
        data = {
            "picture": open('./upload/b64img.txt', 'r').read()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)

        # Fake authenticate and try again
        user = get_new_user()
        self.client.force_authenticate(user)  # pylint: disable=E1101

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
        url = '/api/upload'
        image = lambda: SimpleUploadedFile(
            "img.jpg", open("./upload/img.jpg", "rb").read(), content_type="image/jpeg")
        response = self.client.post(url, {'picture': image()})

        # Check if the file was uploaded
        img_id = response.data['id']
        img = UploadedImage.objects.get(pk=img_id)
        self.assertIn('.jpg', str(img.picture))

        # Check clean images chore
        res1 = self.client.post(url, {'picture': image()})

        # Create images more than an hour ago
        with freeze_time(timezone.now() - timedelta(hours=3)):
            res2 = self.client.post(url, {'picture': image()})
            res3 = self.client.post(url, {'picture': image()})
            res4 = self.client.post(url, {'picture': image()})

            event1 = create_event(image_url=res3.data['picture'])
            body1 = create_body(image_url=res4.data['picture'])

        # Get path for checking deletion
        path1 = UploadedImage.objects.get(pk=res1.data['id']).picture.path
        path2 = UploadedImage.objects.get(pk=res2.data['id']).picture.path

        # Call the chore
        clean = lambda: call_command('clean-images')
        clean()

        # Check if unclaimed images were removed
        img_exists = lambda res: UploadedImage.objects.filter(pk=res.data['id']).exists()
        self.assertTrue(img_exists(res1))
        self.assertFalse(img_exists(res2))
        self.assertTrue(img_exists(res3))
        self.assertTrue(img_exists(res4))

        # Check if file is deleted
        self.assertTrue(isfile(path1))
        self.assertFalse(isfile(path2))

        # Check after invalidating claimant
        body1.image_url = 'https://insti.app'
        body1.save()
        clean()
        self.assertTrue(img_exists(res3))
        self.assertFalse(img_exists(res4))

        # Check after deleting claimant
        event1.delete()
        clean()
        self.assertFalse(img_exists(res3))
