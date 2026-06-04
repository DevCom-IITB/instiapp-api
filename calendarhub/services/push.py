try:
    from firebase_admin import messaging
except ImportError:
    messaging = None


def _build_message(token, title, body, data):
    android = messaging.AndroidConfig(
        priority='high',
        notification=messaging.AndroidNotification(
            title=title, body=body, sound='default'
        ),
    )
    # iOS requires APNSConfig for sound and high-priority delivery
    apns = messaging.APNSConfig(
        headers={'apns-priority': '10'},
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                alert=messaging.ApsAlert(title=title, body=body),
                sound='default',
                content_available=True,
            )
        ),
    )
    return messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body),
        android=android,
        apns=apns,
        data=data,
    )


class PushService:
    def send_to_user(self, user, payload):
        """Send a push notification to all of a user's registered devices."""
        if messaging is None:
            return

        title = payload.get('title', '')
        body = payload.get('body', '')
        data = {k: str(v) for k, v in payload.get('data', {}).items()}

        # Collect tokens from all active devices
        from other.models import Device
        tokens = list(
            Device.objects.filter(user=user)
            .exclude(fcm_id=None)
            .exclude(fcm_id='')
            .values_list('fcm_id', 'platform')
        )

        # Fall back to the legacy single token on UserProfile
        if not tokens:
            fcm_id = getattr(user, 'fcm_id', None)
            if fcm_id:
                tokens = [(fcm_id, '')]

        for token, _ in tokens:
            try:
                msg = _build_message(token, title, body, data)
                messaging.send(msg)
            except Exception as ex:
                print(f'Push send failed for user {user.id} token {token[:10]}…: {ex}')


push_service = PushService()
