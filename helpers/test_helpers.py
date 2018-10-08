"""Helpers for creation of objects in tests."""
from datetime import timedelta
from django.utils import timezone
from bodies.models import Body
from events.models import Event
from users.models import UserTag
from users.models import UserTagCategory

def create_event(start_time_delta=0, end_time_delta=0, name='Event'):
    """Create an event with optional start and end times."""
    create_event.i += 1
    return Event.objects.create(
        name=name + str(create_event.i) if name == 'Event' else name,
        start_time=timezone.now() + timedelta(hours=start_time_delta),
        end_time=timezone.now() + timedelta(hours=end_time_delta))
create_event.i = 0

def create_body():
    """Create a test body."""
    create_body.i += 1
    return Body.objects.create(name='TestBody' + str(create_body.i))
create_body.i = 0

def create_usertagcategory(name=None):
    """Create a test tag category."""
    create_usertagcategory.i += 1
    return UserTagCategory.objects.create(
        name='TestCategory %s' % create_body.i if not name else name)
create_usertagcategory.i = 0

def create_usertag(category, regex, target='hostel', name='tag'):
    """Create a test tag."""
    create_usertag.i += 1
    return UserTag.objects.create(
        name=name + str(create_usertag.i) if name == 'tag' else name,
        category=category, target=target, regex=regex)
create_usertag.i = 0
