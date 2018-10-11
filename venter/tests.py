from rest_framework.test import APITestCase
from login.tests import get_new_user
from venter.models import Complaints, TagUris, Comment, ComplaintMedia


class VenterTestCase(APITestCase):
    """Unit tests for venter."""

    def setUp(self):
        self.user = get_new_user()
        self.client.force_authenticate(self.user)  # pylint: disable=E1101

    def test_complaint_get(self):
        """Test getting venter complaint lists."""

        def create_complaint(user, **kwargs):
            Complaints.objects.create(created_by=user, **kwargs)

        create_complaint(self.user.profile)
        create_complaint(get_new_user().profile)
        create_complaint(self.user.profile, status='Deleted')

        url = '/api/venter/complaints'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        url = '/api/venter/complaints?filter=me'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_tags_get(self):

        TagUris.objects.create(tag_uri='garbage')
        TagUris.objects.create(tag_uri='Stray dogs')

        url = '/api/venter/tags'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        url = '/api/venter/tags?tags=gar'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    # pylint: disable=R0915
    def test_complaint(self):
        """ Test all public methods of venter complaint."""
        url = '/api/venter/complaints'
        TagUris.objects.create(tag_uri='garbage')
        data = {
            'description': 'test',
            'tags': ['flexes', 'garbage'],
            'images': [
                'https://www.google.com/',
                'https://www.facebook.com/'
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['images']), 2)
        self.assertEqual(len(response.data['tags']), 2)

        data = {
            'description': 'test',
            'tags': ['Stray Dogs', 'Potholes'],
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['images']), 0)
        self.assertEqual(len(response.data['tags']), 2)

        url = '/api/venter/complaints?filter=me'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        url = '/api/venter/complaints?search=te'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        url = '/api/venter/complaints?search'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        url = '/api/venter/complaints?tags'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

        url = '/api/venter/complaints?tags=stra'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        url = '/api/venter/complaints?tags=stra&tags=Po'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        cid = str(response.data[0]['id'])
        url = '/api/venter/complaints/' + cid
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], 'test')

        url = '/api/venter/complaints/' + cid + '/upvote'

        # No Action
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

        url += '?action='

        # Invalid Action
        response = self.client.get(url + 'k')
        self.assertEqual(response.status_code, 400)

        # UpVote
        response = self.client.get(url + '1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['users_up_voted']), 1)

        # UnUpVote
        response = self.client.get(url + '0')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['users_up_voted']), 0)

    def test_comment(self):
        """Test all public venter comment APIs."""

        complaint = Complaints.objects.create(created_by=self.user.profile)

        url = '/api/venter/complaints/' + str(complaint.id) + '/comments'

        data = {'text': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        cid = str(response.data['id'])
        url = '/api/venter/comments/' + cid
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['text'], 'test')

        data = {'text': 'test2'}

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['text'], 'test2')

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 204)

        comment = Comment.objects.create(
            complaint=complaint,
            text='test_comment',
            commented_by=get_new_user().profile
        )
        url = '/api/venter/comments/' + str(comment.id)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_model_venter(self):
        """Run other model tests for venter."""

        complaint = Complaints.objects.create(
            created_by=self.user.profile,
            description='test'
        )

        self.assertEqual(str(complaint), 'test')

        tag = TagUris.objects.create(
            tag_uri='test_tag'
        )

        self.assertEqual(str(tag), 'test_tag')

        comment = Comment.objects.create(
            complaint=complaint,
            text='test_comment',
            commented_by=self.user.profile
        )

        self.assertEqual(str(comment), 'test_comment')

        complaintMedia = ComplaintMedia.objects.create(
            complaint=complaint,
            image_url='www.google.com'
        )

        self.assertEqual(str(complaintMedia), 'www.google.com')
