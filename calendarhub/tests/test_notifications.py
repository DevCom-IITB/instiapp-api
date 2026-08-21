from datetime import timedelta
from unittest.mock import patch, MagicMock, call

from django.test import TestCase
from django.utils.timezone import now

from calendarhub.tasks.notifications import (
    send_event_reminder,
    send_change_notification,
    schedule_reminder,
    cancel_reminder,
    cancel_reminder_by_external_id,
)
from calendarhub.services.push import PushService


def _make_user(user_id='user-1'):
    user = MagicMock()
    user.id = user_id
    return user


def _no_prefs():
    """Simulate no CalendarSourcePreference row — notifications default ON."""
    m = MagicMock()
    m.return_value.first.return_value = None
    return m


def _prefs(notifications_enabled):
    """Simulate a CalendarSourcePreference row with a specific setting."""
    pref = MagicMock()
    pref.notifications_enabled = notifications_enabled
    m = MagicMock()
    m.return_value.first.return_value = pref
    return m


class SendEventReminderTests(TestCase):

    @patch('calendarhub.services.push.push_service')
    def test_sends_notification(self, mock_push):
        user = _make_user()
        with patch('users.models.UserProfile.objects.get', return_value=user), \
             patch('calendarhub.models.CalendarSourcePreference.objects.filter', _no_prefs()):
            send_event_reminder.apply(args=['user-1', 'uid:123', 'Math Exam', 'instiapp'])

        mock_push.send_to_user.assert_called_once()
        payload = mock_push.send_to_user.call_args[0][1]
        self.assertEqual(payload['title'], 'Starting in 30 minutes')
        self.assertEqual(payload['body'], 'Math Exam')
        self.assertEqual(payload['data']['source'], 'instiapp')

    @patch('calendarhub.services.push.push_service')
    def test_skips_when_notifications_disabled(self, mock_push):
        user = _make_user()
        with patch('users.models.UserProfile.objects.get', return_value=user), \
             patch('calendarhub.models.CalendarSourcePreference.objects.filter', _prefs(False)):
            send_event_reminder.apply(args=['user-1', 'uid:123', 'Math Exam', 'instiapp'])

        mock_push.send_to_user.assert_not_called()

    @patch('calendarhub.services.push.push_service')
    def test_sends_when_notifications_enabled(self, mock_push):
        user = _make_user()
        with patch('users.models.UserProfile.objects.get', return_value=user), \
             patch('calendarhub.models.CalendarSourcePreference.objects.filter', _prefs(True)):
            send_event_reminder.apply(args=['user-1', 'uid:123', 'Lab', 'instiapp'])

        mock_push.send_to_user.assert_called_once()

    @patch('calendarhub.services.push.push_service')
    def test_resobin_skips_cancelled_event(self, mock_push):
        """If the resobin event is cancelled (or missing) since scheduling, do not send."""
        user = _make_user()
        cache_qs = MagicMock()
        cache_qs.exists.return_value = False  # event cancelled/missing

        with patch('users.models.UserProfile.objects.get', return_value=user), \
             patch('calendarhub.models.CalendarSourcePreference.objects.filter', _no_prefs()), \
             patch('calendarhub.models.ExternalCalendarEventCache.objects.filter', return_value=cache_qs):
            # uid format: resobin:<subsource>:<external_id>
            send_event_reminder.apply(args=['user-1', 'resobin:exam:42', 'Physics', 'resobin'])

        mock_push.send_to_user.assert_not_called()

    @patch('calendarhub.services.push.push_service')
    def test_resobin_sends_active_event(self, mock_push):
        user = _make_user()
        cache_qs = MagicMock()
        cache_qs.exists.return_value = True  # event still active

        with patch('users.models.UserProfile.objects.get', return_value=user), \
             patch('calendarhub.models.CalendarSourcePreference.objects.filter', _no_prefs()), \
             patch('calendarhub.models.ExternalCalendarEventCache.objects.filter', return_value=cache_qs):
            send_event_reminder.apply(args=['user-1', 'resobin:exam:42', 'Physics', 'resobin'])

        mock_push.send_to_user.assert_called_once()
        payload = mock_push.send_to_user.call_args[0][1]
        self.assertEqual(payload['data']['event_uid'], 'resobin:exam:42')

    @patch('calendarhub.services.push.push_service')
    def test_resobin_uid_without_external_id_still_sends(self, mock_push):
        """uid with fewer than 3 parts → external_id is None → skip cache check, send anyway."""
        user = _make_user()
        with patch('users.models.UserProfile.objects.get', return_value=user), \
             patch('calendarhub.models.CalendarSourcePreference.objects.filter', _no_prefs()):
            send_event_reminder.apply(args=['user-1', 'resobin:only-two', 'Physics', 'resobin'])

        mock_push.send_to_user.assert_called_once()


class SendChangeNotificationTests(TestCase):

    @patch('calendarhub.services.push.push_service')
    def test_sends_for_each_notify_worthy_type(self, mock_push):
        user = _make_user()
        worthy = [
            ('exam_added', 'New exam added'),
            ('exam_modified', 'Exam time or location changed'),
            ('exam_cancelled', 'Exam cancelled'),
            ('slot_cancelled', 'Class cancelled'),
            ('slot_modified', 'Class time or location changed'),
            ('deadline_added', 'New deadline added'),
        ]
        for change_type, expected_title in worthy:
            mock_push.reset_mock()
            with patch('users.models.UserProfile.objects.get', return_value=user), \
                 patch('calendarhub.models.CalendarSourcePreference.objects.filter', _no_prefs()):
                send_change_notification.apply(args=['user-1', change_type, 'Some Subject'])

            mock_push.send_to_user.assert_called_once()
            payload = mock_push.send_to_user.call_args[0][1]
            self.assertEqual(payload['title'], expected_title, f'Wrong title for {change_type}')
            self.assertEqual(payload['body'], 'Some Subject')
            self.assertEqual(payload['data']['change_type'], change_type)

    @patch('calendarhub.services.push.push_service')
    def test_ignores_non_notify_worthy_type(self, mock_push):
        user = _make_user()
        with patch('users.models.UserProfile.objects.get', return_value=user), \
             patch('calendarhub.models.CalendarSourcePreference.objects.filter', _no_prefs()):
            send_change_notification.apply(args=['user-1', 'unknown_event', 'Something'])

        mock_push.send_to_user.assert_not_called()

    @patch('calendarhub.services.push.push_service')
    def test_skips_when_notifications_disabled(self, mock_push):
        user = _make_user()
        with patch('users.models.UserProfile.objects.get', return_value=user), \
             patch('calendarhub.models.CalendarSourcePreference.objects.filter', _prefs(False)):
            send_change_notification.apply(args=['user-1', 'exam_added', 'Maths'])

        mock_push.send_to_user.assert_not_called()


class ScheduleReminderTests(TestCase):

    @patch('calendarhub.tasks.notifications.send_event_reminder')
    def test_schedules_future_event(self, mock_task):
        future = now() + timedelta(hours=2)
        schedule_reminder('uid:1', 'user-1', future, 'Lecture', 'instiapp')

        mock_task.apply_async.assert_called_once()
        kwargs = mock_task.apply_async.call_args[1]
        self.assertEqual(kwargs['task_id'], 'reminder:uid:1:user-1')
        self.assertEqual(kwargs['eta'], future - timedelta(minutes=30))

    @patch('calendarhub.tasks.notifications.send_event_reminder')
    def test_skips_past_event(self, mock_task):
        """Fire time already passed — should not schedule anything."""
        past = now() - timedelta(hours=1)
        schedule_reminder('uid:2', 'user-1', past, 'Old Lecture', 'instiapp')

        mock_task.apply_async.assert_not_called()

    @patch('calendarhub.tasks.notifications.send_event_reminder')
    def test_skips_event_starting_in_less_than_30_minutes(self, mock_task):
        soon = now() + timedelta(minutes=10)
        schedule_reminder('uid:3', 'user-1', soon, 'Imminent Lecture', 'instiapp')

        mock_task.apply_async.assert_not_called()


class CancelReminderTests(TestCase):

    @patch('backend.celery.app')
    def test_revokes_task(self, mock_app):
        cancel_reminder('uid:1', 'user-1')
        mock_app.control.revoke.assert_called_once_with('reminder:uid:1:user-1')

    @patch('backend.celery.app')
    def test_cancel_by_external_id_revokes_all_subsources(self, mock_app):
        cancel_reminder_by_external_id('user-1', '42')

        expected_subsources = ('class', 'tutorial', 'lab', 'exam', 'deadline', 'other')
        calls = mock_app.control.revoke.call_args_list
        self.assertEqual(len(calls), len(expected_subsources))
        for subsource, c in zip(expected_subsources, calls):
            self.assertEqual(c, call(f'reminder:resobin:{subsource}:42:user-1'))


class PushServiceTests(TestCase):
    """Tests for PushService.send_to_user — exercises push.py directly."""

    def _make_payload(self):
        return {'title': 'Test Title', 'body': 'Test Body', 'data': {'key': 'value'}}

    @patch('calendarhub.services.push.messaging')
    @patch('other.models.Device.objects')
    def test_sends_to_all_devices(self, mock_device_objects, mock_messaging):
        """Every device token for the user gets a separate Firebase send call."""
        user = _make_user()
        mock_device_objects.filter.return_value.exclude.return_value.exclude.return_value.values_list.return_value = [
            ('token-android', 'android'),
            ('token-ios', 'ios'),
        ]

        PushService().send_to_user(user, self._make_payload())

        self.assertEqual(mock_messaging.send.call_count, 2)

    @patch('calendarhub.services.push.messaging')
    @patch('other.models.Device.objects')
    def test_message_includes_android_and_apns_config(self, mock_device_objects, mock_messaging):
        """Built message must carry both AndroidConfig and APNSConfig for cross-platform delivery."""
        user = _make_user()
        mock_device_objects.filter.return_value.exclude.return_value.exclude.return_value.values_list.return_value = [
            ('token-1', 'android'),
        ]

        PushService().send_to_user(user, self._make_payload())

        built_msg = mock_messaging.Message.call_args[1]
        self.assertIsNotNone(built_msg.get('android'), 'AndroidConfig missing')
        self.assertIsNotNone(built_msg.get('apns'), 'APNSConfig missing — iOS will not get sound/priority')

    @patch('calendarhub.services.push.messaging')
    @patch('other.models.Device.objects')
    def test_data_values_are_stringified(self, mock_device_objects, mock_messaging):
        """Firebase requires all data payload values to be strings."""
        user = _make_user()
        mock_device_objects.filter.return_value.exclude.return_value.exclude.return_value.values_list.return_value = [
            ('token-1', 'android'),
        ]
        payload = {'title': 'T', 'body': 'B', 'data': {'count': 5, 'flag': True, 'uid': None}}

        PushService().send_to_user(user, payload)

        passed_data = mock_messaging.Message.call_args[1]['data']
        for v in passed_data.values():
            self.assertIsInstance(v, str, f'Data value {v!r} is not a string')

    @patch('calendarhub.services.push.messaging')
    @patch('other.models.Device.objects')
    def test_falls_back_to_userprofile_fcm_id(self, mock_device_objects, mock_messaging):
        """When no Device rows exist, use the legacy fcm_id on UserProfile."""
        user = _make_user()
        user.fcm_id = 'legacy-token'
        mock_device_objects.filter.return_value.exclude.return_value.exclude.return_value.values_list.return_value = []

        PushService().send_to_user(user, self._make_payload())

        mock_messaging.send.assert_called_once()

    @patch('calendarhub.services.push.messaging')
    @patch('other.models.Device.objects')
    def test_sends_nothing_when_no_tokens_at_all(self, mock_device_objects, mock_messaging):
        """No Device rows and no fcm_id → nothing sent."""
        user = _make_user()
        user.fcm_id = None
        mock_device_objects.filter.return_value.exclude.return_value.exclude.return_value.values_list.return_value = []

        PushService().send_to_user(user, self._make_payload())

        mock_messaging.send.assert_not_called()

    @patch('calendarhub.services.push.messaging', None)
    def test_noop_when_firebase_not_installed(self):
        """If firebase_admin is not installed, send_to_user returns silently."""
        user = _make_user()
        # Should not raise even though messaging is None
        PushService().send_to_user(user, self._make_payload())

    @patch('calendarhub.services.push.messaging')
    @patch('other.models.Device.objects')
    def test_one_failed_token_does_not_block_others(self, mock_device_objects, mock_messaging):
        """A Firebase error for one device must not prevent sending to the rest."""
        user = _make_user()
        mock_device_objects.filter.return_value.exclude.return_value.exclude.return_value.values_list.return_value = [
            ('bad-token', 'android'),
            ('good-token', 'ios'),
        ]
        mock_messaging.send.side_effect = [Exception('invalid token'), None]

        PushService().send_to_user(user, self._make_payload())

        self.assertEqual(mock_messaging.send.call_count, 2)
