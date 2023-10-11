"""Helpers for creation of objects in tests."""
from datetime import timedelta
from django.utils import timezone
from bodies.models import Body
from events.models import Event
from users.models import UserTag
from users.models import UserTagCategory
from community.models import Community, CommunityPost


def create_event(start_time_delta=0, end_time_delta=0, **kwargs):
    """Create an event with optional start and end times."""
    create_event.i += 1

    # Fallback for name
    if "name" not in kwargs:
        kwargs["name"] = "Event %d" % create_event.i

    # Create new object
    return Event.objects.create(
        start_time=timezone.now() + timedelta(hours=start_time_delta),
        end_time=timezone.now() + timedelta(hours=end_time_delta),
        **kwargs
    )


def create_body(**kwargs):
    """Create a test body."""
    create_body.i += 1
    if "name" not in kwargs:
        kwargs["name"] = "TestBody%d" % create_body.i
    return Body.objects.create(**kwargs)


def create_community(**kwargs):
    """Create a test body."""
    create_community.i += 1
    if "name" not in kwargs:
        kwargs["name"] = "TestCommunity%d" % create_community.i
    if "body" not in kwargs:
        kwargs["body"] = create_body()
    return Community.objects.create(**kwargs)


def create_communitypost(**kwargs):
    """Create a test body."""
    if "posted_by" not in kwargs:
        raise Exception("Must specify posted_by")

    create_communitypost.i += 1
    if "content" not in kwargs:
        kwargs["content"] = "TestCommunityPostContent%d" % create_communitypost.i
    if "community" not in kwargs:
        kwargs["community"] = create_community()
    return CommunityPost.objects.create(**kwargs)


def create_usertagcategory(name=None):
    """Create a test tag category."""
    create_usertagcategory.i += 1
    return UserTagCategory.objects.create(
        name="TestCategory %s" % create_body.i if not name else name
    )


def create_usertag(category, regex, target="hostel", name="tag", **kwargs):
    """Create a test tag."""
    create_usertag.i += 1
    return UserTag.objects.create(
        name=name + str(create_usertag.i) if name == "tag" else name,
        category=category,
        target=target,
        regex=regex,
        **kwargs
    )


create_event.i = 0
create_body.i = 0
create_community.i = 0
create_communitypost.i = 0
create_usertagcategory.i = 0
create_usertag.i = 0
