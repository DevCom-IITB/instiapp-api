"""Unit tests for upload."""
from rest_framework.test import APITestCase
from login.tests import get_new_user
from upload.models import UploadedImage

class UploadTestCase(APITestCase):
    """Check if logged in users can upload files."""

    def test_upload(self):
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
