from rest_framework.test import APITestCase
from login.tests import get_new_user
from venter.models import Complaints, TagUris, Comment, ComplaintMedia


class VenterTestCase(APITestCase):
    def setUp(self):
        self.user = get_new_user()
        self.client.force_authenticate(self.user)

    def test_complaint_get(self):
        Complaints.objects.create(created_by=self.user.profile)
        Complaints.objects.create(created_by=get_new_user().profile)
        Complaints.objects.create(created_by=self.user.profile, status="Deleted")

        url = '/api/complaints'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        url = '/api/complaints?filter=me'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_complaint(self):
        url = '/api/complaints'

        TagUris.objects.create(tag_uri='garbage')
        data = {
            'description': 'test',
            'tags':["flexes", "garbage"],
            'images': [
                "https://www.google.com/",
                "https://www.facebook.com/"
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['images']), 2)
        self.assertEqual(len(response.data['tags']), 2)

        data = {
            'description': 'test',
            'tags': [],
            'images': []
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['images']), 0)
        self.assertEqual(len(response.data['tags']), 0)

        url = '/api/complaints?filter=me'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        cid = str(response.data[0]['id'])
        url = '/api/complaints/' + cid
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], 'test')

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['users_up_voted']), 1)

    def test_comment(self):
        complaint = Complaints.objects.create(created_by=self.user.profile)

        url = '/api/complaints/' + str(complaint.id) + '/comments'

        data = {
            'text': "test"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        cid = str(response.data['id'])
        url = '/api/comments/' + cid
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['text'], 'test')

        data = {
            'text': "test2"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['text'], 'test2')

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 204)

        comment = Comment.objects.create(
            complaint=complaint,
            text="test_comment",
            commented_by=get_new_user().profile
        )
        url = '/api/comments/' + str(comment.id)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_model_venter(self):
        complaint = Complaints.objects.create(
            created_by=self.user.profile,
            description="test"
        )

        self.assertEqual(str(complaint), 'test')

        tag = TagUris.objects.create(
            tag_uri="test_tag"
        )

        self.assertEqual(str(tag), 'test_tag')

        comment = Comment.objects.create(
            complaint=complaint,
            text="test_comment",
            commented_by=self.user.profile
        )

        self.assertEqual(str(comment), 'test_comment')

        complaintMedia = ComplaintMedia.objects.create(
            complaint=complaint,
            image_url="www.google.com"
        )

        self.assertEqual(str(complaintMedia), 'www.google.com')
