from types import SimpleNamespace
from django.core import mail
from django.contrib.admin.sites import AdminSite
from rest_framework.test import APITestCase, APIClient
from login.tests import get_new_user
from venter.admin import ComplaintModelAdmin
from venter.models import Complaint
from venter.models import ComplaintTag
from venter.models import ComplaintComment
from venter.models import ComplaintImage
from venter.models import ComplaintAuthority

# Status variables for complaints
STATUS_REPORTED = 'Reported'
STATUS_IN_PROGRESS = 'In Progress'
STATUS_RESOLVED = 'Resolved'
STATUS_DELETED = 'Deleted'

class VenterTestCase(APITestCase):
    """Unit tests for venter."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_new_user()
        self.client.force_authenticate(self.user)

    def test_complaint_get(self):
        """Test getting venter complaint lists."""

        def create_complaint(user, **kwargs):
            Complaint.objects.create(created_by=user, **kwargs)

        # Creating 4 dummy complaints, one of which has a "DELETED" status
        create_complaint(self.user.profile)
        create_complaint(get_new_user().profile)
        create_complaint(get_new_user().profile)
        create_complaint(self.user.profile, status=STATUS_DELETED)

        url = '/api/venter/complaints'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        url = '/api/venter/complaints?from=0&num=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        url = '/api/venter/complaints?filter=me'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_tags_get(self):
        """ Test all tags or particular tag return."""

        ComplaintTag.objects.create(tag_uri='garbage')
        ComplaintTag.objects.create(tag_uri='Stray dogs')

        url = '/api/venter/tags'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        url = '/api/venter/tags?tags=gar'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_complaint(self):  # pylint: disable=R0915
        """ Test all public methods of venter complaint."""
        # Testing complaint POST requests
        base_url = '/api/venter/complaints'
        ComplaintTag.objects.create(tag_uri='garbage')
        data = {
            'description': 'test',
            'tags': ['flexes', 'garbage'],
            'images': [
                'https://www.google.com/',
                'https://www.facebook.com/'
            ]
        }

        response = self.client.post(base_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['images']), 2)
        self.assertEqual(len(response.data['tags']), 2)

        # Creator should be auto-subscribed to the complaint
        response = self.client.get(base_url)
        self.assertEqual(response.data[0]['is_subscribed'], True)

        data = {
            'description': 'test',
            'tags': ['Stray Dogs', 'Potholes'],
        }

        response = self.client.post(base_url, data, format='json')
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

        # Retreiving complaint id (cid)
        cid = str(response.data[0]['id'])
        complaint_url = '/api/venter/complaints/' + cid
        response = self.client.get(complaint_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], 'test')

        # Test for complaint upvoting
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

        # Verify the addition of the user to the array for 'users_up_voted'
        self.assertEqual(len(response.data['users_up_voted']), 1)

        # Verify user's upvote status for the complaint
        response = self.client.get(complaint_url)
        self.assertEqual(response.data['upvoted'], True)

        # UnUpVote
        response = self.client.get(url + '0')
        self.assertEqual(response.status_code, 200)

        # Verify the removal of the user from the 'users_up_voted' array
        self.assertEqual(len(response.data['users_up_voted']), 0)

        # Verify user's upvote status for the complaint
        response = self.client.get(complaint_url)
        self.assertEqual(response.data['upvoted'], False)

        # Test for Complaint Subscription
        url = '/api/venter/complaints/' + cid + '/subscribe'

        # No Action
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

        url += '?action='

        # Invalid Action
        response = self.client.get(url + 'k')
        self.assertEqual(response.status_code, 400)

        # Subscribe
        response = self.client.get(url + '1')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(complaint_url)
        self.assertEqual(response.data['is_subscribed'], True)

        # UnSubscribe
        response = self.client.get(url + '0')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(complaint_url)
        self.assertEqual(response.data['is_subscribed'], False)

    def test_comment(self):
        """Test all public venter comment APIs."""
        # Dummy complaint, created by 'user'. The creator is already subscribed to the complaint
        complaint = Complaint.objects.create(created_by=self.user.profile)
        complaint.subscriptions.add(self.user.profile)

        # Creating a new user and profile to make a comment and test auto-subscription of comments
        test_commenter_1 = get_new_user()
        self.client.force_authenticate(user=test_commenter_1)

        url = '/api/venter/complaints/' + str(complaint.id) + '/comments'

        data = {'text': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        cid = str(response.data['id'])

        # Testing whether commenter is auto-subscribed to the complaint, and is the most recent subscriber
        url = '/api/venter/complaints/' + str(complaint.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['is_subscribed'], True)

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

        comment = ComplaintComment.objects.create(
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

        complaint = Complaint.objects.create(
            created_by=self.user.profile,
            description='test'
        )

        self.assertEqual(str(complaint), 'test')

        tag = ComplaintTag.objects.create(
            tag_uri='test_tag'
        )

        self.assertEqual(str(tag), 'test_tag')

        comment = ComplaintComment.objects.create(
            complaint=complaint,
            text='test_comment',
            commented_by=self.user.profile
        )

        self.assertEqual(str(comment), 'test_comment')

        complaintMedia = ComplaintImage.objects.create(
            complaint=complaint,
            image_url='www.google.com'
        )

        self.assertEqual(str(complaintMedia), 'www.google.com')

        authority = ComplaintAuthority.objects.create(
            name='dummyauth',
            email='dummyauth@example.com'
        )

        self.assertEqual(str(authority), 'dummyauth <dummyauth@example.com>')

        complaint.authorities.add(authority)

        self.assertEqual(len(Complaint.email_list(complaint)), 1)

    def test_admin_actions(self):
        complaint_admin = ComplaintModelAdmin(Complaint, AdminSite())
        request = SimpleNamespace()

        Complaint.objects.create(created_by=self.user.profile, status=STATUS_REPORTED)
        queryset = Complaint.objects.filter(status=STATUS_REPORTED)
        complaint_admin.mark_as_resolved(complaint_admin, request, queryset)
        self.assertEqual(Complaint.objects.get(status=STATUS_RESOLVED).status, STATUS_RESOLVED)

        Complaint.objects.create(created_by=self.user.profile, status=STATUS_REPORTED)
        queryset = Complaint.objects.filter(status=STATUS_REPORTED)
        complaint_admin.mark_as_in_progress(complaint_admin, request, queryset)
        self.assertEqual(Complaint.objects.get(status=STATUS_IN_PROGRESS).status, STATUS_IN_PROGRESS)

        Complaint.objects.create(created_by=self.user.profile, status=STATUS_REPORTED)
        queryset = Complaint.objects.filter(status=STATUS_REPORTED)
        complaint_admin.mark_as_deleted(complaint_admin, request, queryset)
        self.assertEqual(Complaint.objects.get(status=STATUS_DELETED).status, STATUS_DELETED)

    def test_send_mass_mail(self):
        complaint_admin = ComplaintModelAdmin(Complaint, AdminSite())
        request = SimpleNamespace()

        # Adding dummy recipients for emails
        auth_mail_1 = ComplaintAuthority.objects.create(email='receiver1@example.com', name='receiver1')
        auth_mail_2 = ComplaintAuthority.objects.create(email='receiver2@example.com', name='receiver2')

        # Reported Complaint (multiple recipients)
        complaint_multi = Complaint.objects.create(
            created_by=self.user.profile, status=STATUS_REPORTED, description='Test Complaint')
        complaint_multi.authorities.add(auth_mail_1, auth_mail_2)

        # In Progress Complaint with images (single recipient)
        complaint_single = Complaint.objects.create(created_by=self.user.profile, status=STATUS_IN_PROGRESS)
        complaint_single.authorities.add(auth_mail_1)
        image = []
        image.append(ComplaintImage.objects.create(image_url='https://www.google.com/', complaint=complaint_single))
        complaint_single.images.set(image)

        # Complaint with no authority
        Complaint.objects.create(created_by=self.user.profile, status=STATUS_REPORTED)
        authority_list = set(complaint_multi.authorities.values_list('email', flat=True))

        # Test if the email shows up in the outbox when method is called
        queryset = Complaint.objects.filter(status=STATUS_REPORTED)
        complaint_admin.send_emails(complaint_admin, request, queryset)
        self.assertEqual(len(mail.outbox), 1)
        queryset = Complaint.objects.filter(status=STATUS_IN_PROGRESS)
        complaint_admin.send_emails(complaint_admin, request, queryset)
        self.assertEqual(len(mail.outbox), 2)

        # Test for email_sent_to list
        Complaint.objects.create(created_by=self.user.profile, description='multiple')
        new_auth3 = ComplaintAuthority.objects.create(email='auth3@example.com', name='auth3')
        complaint_multival = Complaint.objects.get(description='multiple')
        complaint_multival.authorities.add(new_auth3)
        queryset = Complaint.objects.filter(description='multiple')
        complaint_admin.send_emails(complaint_admin, request, queryset)
        complaint_multival = Complaint.objects.get(description='multiple')
        self.assertEqual(str(complaint_multival.email_sent_to), 'auth3')

        # Test for email_sent_to for new authorities added
        new_auth2 = ComplaintAuthority.objects.create(email='auth2@example.com', name='auth2')
        complaint_multival.authorities.add(new_auth2)
        queryset = Complaint.objects.filter(description='multiple')
        complaint_admin.send_emails(complaint_admin, request, queryset)
        complaint_multival = Complaint.objects.get(description='multiple')
        self.assertEqual(str(complaint_multival.email_sent_to), 'auth3, auth2')

        # Evaluating whether the correct number of recipients are being addressed in the multi recipient complaint
        self.assertEqual(len(mail.outbox[0].to), 2)
        self.assertEqual(set(mail.outbox[0].to), authority_list)
