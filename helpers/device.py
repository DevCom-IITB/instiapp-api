"""Helpers for notification device model."""
from django.db.models import Q
from django.utils import timezone
from django.contrib.sessions.models import Session
from other.models import Device


def update_fcm_device(request, fcm_id):
    """Create or update device."""
    if not request.user.is_authenticated or not fcm_id:  # pragma: no cover
        return

    profile = request.user.profile
    sess = Session.objects.get(pk=request.session.session_key)
    devices = Device.objects.filter(Q(session=sess) | Q(fcm_id=fcm_id))
    device = Device()

    # Check if device is to be updated
    if devices.exists():
        device = devices[0]

        # Delete multiple matches
        for dev in devices[1:]:
            dev.delete()

    # Populate device
    device.session = sess
    device.last_ping = timezone.now()
    device.user = profile
    device.fcm_id = fcm_id
    device.save()

    # Reset for existing devices
    profile.fcm_id = ""
    profile.save()



