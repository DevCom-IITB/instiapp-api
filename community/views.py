from collections import UserList
from pickle import GET
from unicodedata import name
from uuid import UUID
from bodies.models import Body
from users.models import UserProfile
from locations.models import Location
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from community.models import Community
from community.models import CommunityPost
from community.serializer_min import CommunitySerializerMin,CommunityPostSerializerMin
from community.serializers import CommunitySerializers,CommunityPostSerializers
from events.prioritizer import get_fresh_prioritized_events
from events.prioritizer import get_prioritized
from events.serializers import EventSerializer
from events.serializers import EventFullSerializer
from events.models import Event
from roles.helpers import user_has_privilege
from roles.helpers import login_required_ajax
from roles.helpers import forbidden_no_privileges, diff_set
from locations.helpers import create_unreusable_locations
from helpers.misc import query_from_num
from helpers.misc import query_search

class ModeratorViewSet(viewsets.ModelViewSet):
    queryset = CommunityPost.objects
    serializer_class = CommunityPostSerializers
    serializer_class_min = CommunityPostSerializerMin
    
class PostViewSet(viewsets.ModelViewSet):
    """Post"""

    queryset = CommunityPost.objects
    serializer_class = CommunityPostSerializers
    serializer_class_min = CommunityPostSerializerMin
    def get_serializer_context(self):
        return {'request': self.request}

    def retrieve_full(self, request, pk):
        """Get full Post.
        Get by `uuid` or `str_id`"""

        self.queryset = CommunityPostSerializers.setup_eager_loading(self.queryset, request)
        post = self.get_community_post(pk)
        serialized = CommunityPostSerializers(post, context={'request': request}).data

        return Response(serialized)
    
    def retrieve_min(self, request, pk):
        """Get min Post.
        Get by `uuid` or `str_id`"""

        self.queryset = CommunityPostSerializerMin.setup_eager_loading(self.queryset, request)
        post = self.get_community_post(pk)
        serialized = CommunityPostSerializerMin(post, context={'request': request}).data

        return Response(serialized)

    def list(self, request):
        """List Of Posts.
        List fresh posts arranged chronologiaclly for the current user."""

        # Check for time and date filtered query params

        Queryset = CommunityPost.objects.all().order_by("-time_of_modification")
        
        queryset = sorted(Queryset, key=lambda post: post.time_of_modification , reverse=True)
        queryset = query_from_num(request, 20, queryset)

        serializer = CommunityPostSerializerMin(queryset, many=True, context={'request': request})
        data = serializer.data

        return Response({'count': len(data), 'data': data})
    @login_required_ajax
    def create(self, request):
        """Create Post.
        Needs `AddE` permission for each body to be associated."""

        # Prevent posts without any community
        if 'community_id' not in request.data or not request.data['community_id']:
            return forbidden_no_privileges()
        try:
            request.data["content"]
            if request.data["tag_user_call"]:
                 request.data["tag_user_call"]=UserProfile.objects.get(name)                
            if request.data["tag_body_call"]:
                 print(Body.objects.get(name))
            if request.data["tag_location_call"]:
                 print(Location.objects.get(name))            
        except KeyError:
            request.data['content'] = []
            request.data['tag_user_call'] = []
            request.data["tag_body_call"]=[]
            request.data["tag_location_call"]=[]

        return super().create(request)

        
    @login_required_ajax
    def update(self, request, pk):
        """Update Event.
        Needs BodyRole with `UpdE` for at least one associated body.
        Disassociating bodies from the event requires the `DelE`
        permission and associating needs `AddE`"""

        # Prevent events without any body
        if 'bodies_id' not in request.data or not request.data['bodies_id']:
            return forbidden_no_privileges()

        # Get the event currently in database
        event = self.get_community_post(pk)

        # Check if difference in bodies is valid
        if not can_update_bodies(request.data['bodies_id'], event, request.user.profile):
            return forbidden_no_privileges()

        try:
            request.data['event_interest']
            request.data['interests_id']
        except KeyError:
            request.data['event_interest'] = []
            request.data['interests_id'] = []

        return super().update(request, pk)

    @login_required_ajax
    def destroy(self, request, pk):
        """Delete Event.
        Needs `DelE` permission for all associated bodies."""

        event = self.get_community_post(pk)
        if all([user_has_privilege(request.user.profile, str(body.id), 'DelE')
                for body in event.bodies.all()]):
            return super().destroy(request, pk)

        return forbidden_no_privileges()

    def get_community_post(self, pk):
        """Get a community post from pk uuid or strid."""
        try:
            UUID(pk, version=4)
            return get_object_or_404(self.queryset, id=pk)
        except ValueError:
            return get_object_or_404(self.queryset, str_id=pk)


def can_update_bodies(new_bodies_id, event, profile):
    """Check if the user is permitted to change the event bodies to ones given."""

    # Get current and difference in body ids
    old_bodies_id = [str(x.id) for x in event.bodies.all()]
    added_bodies = diff_set(new_bodies_id, old_bodies_id)
    removed_bodies = diff_set(old_bodies_id, new_bodies_id)

    # Check if user can add events for new bodies
    can_add_events = all(
        [user_has_privilege(profile, bid, 'AddE') for bid in added_bodies])

    # Check if user can remove events for removed
    can_del_events = all(
        [user_has_privilege(profile, bid, 'DelE') for bid in removed_bodies])

    # Check if the user can update event for any of the old bodies
    can_update = any(
        [user_has_privilege(profile, bid, 'UpdE') for bid in old_bodies_id])

    return can_add_events and can_del_events and can_update

def get_update_venue_ids(venue_names, event):
    """Get venue ids with minimal object creation for updating event."""

    old_venue_names = [x.name for x in event.venues.all()]
    new_venue_names = venue_names
    added_venues = diff_set(new_venue_names, old_venue_names)
    common_venues = list(set(old_venue_names).intersection(new_venue_names))

    common_venue_ids = [str(x.id) for x in event.venues.filter(name__in=common_venues)]
    added_venue_ids = create_unreusable_locations(added_venues)

    return added_venue_ids + common_venue_ids


class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects
    serializer_class = CommunitySerializers
<<<<<<< HEAD
        
=======

>>>>>>> 5880015eba93eaff1a5dda636028ec8f78281b4a
    def get_serializer_context(self):
        return super().get_serializer_context()

    def list(self, request):
        queryset = Community.objects.all()
        serializer = CommunitySerializerMin(queryset, many=True)
        data = serializer.data
        return Response(data)

    def retrieve(self, request, pk):

        # Prefetch and annotate data
        self.queryset = CommunitySerializers.setup_eager_loading(self.queryset, request)

        # Try UUID or fall back to str_id
        body = self.get_body(pk)

        # Serialize the body
        serialized = CommunitySerializers(body, context={'request': request}).data
        return Response(serialized)

    def get_body(self, pk):
        try:
            UUID(pk, version=4)
            return get_object_or_404(self.queryset, id=pk)
        except ValueError:
            return get_object_or_404(self.queryset, str_id=pk)
