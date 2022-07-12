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
from roles.helpers import user_has_community_privilege
from roles.helpers import login_required_ajax
from roles.helpers import forbidden_no_privileges, diff_set
from locations.helpers import create_unreusable_locations
from helpers.misc import query_from_num
from helpers.misc import query_search

class ModeratorViewSet(viewsets.ModelViewSet):
    serializer_class = CommunityPostSerializers
    serializer_class_min = CommunityPostSerializerMin
    def get_community_post(self, pk):
        """Get a community post from pk uuid or strid."""
        try:
            UUID(pk, version=4)
            return get_object_or_404(self.queryset, id=pk)
        except ValueError:
            return get_object_or_404(self.queryset, str_id=pk)

    @login_required_ajax
    def Delete_post(self,request,pk):
        if all([user_has_privilege(request.user.profile, id, 'ModP')]):
            post = self.get_community_post(pk)
            if post in CommunityPost.objects.all():
                return super().destroy(request, pk)
    @login_required_ajax
    def update_post(self,request,pk):
        post = self.get_community_post(pk)
        if 'community_id' not in request.data or not request.data['community_id']:
            return forbidden_no_privileges()
        CommunityPost.status=0

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

        Queryset = CommunityPost.objects.filter(status=1).order_by("-time_of_modification")
        
        queryset = sorted(Queryset, key=lambda post: post.time_of_modification , reverse=True)
        queryset = query_from_num(request, 20, queryset)

        serializer = CommunityPostSerializerMin(queryset, many=True, context={'request': request})
        data = serializer.data

        return Response({'count': len(data), 'data': data})
    #@login_required_ajax
    def create_post(self, request):
        """Create Post.
        Needs `AddP` permission for each body to be associated."""

        # Prevent posts without any community
        if 'community_id' not in request.data or not request.data['community_id']:
            return forbidden_no_privileges()
        try:
            request.data["status"]=0
            request.data["thread_rank"]=1
            request.data["parent"]=None
            request.data["content"]
            if request.data["tag_user_call"]:
                 request.data["tag_user_call"]=UserProfile.objects.get(name)                
            if request.data["tag_body_call"]:
                 request.data["tag_body_call"]=Body.objects.get(name) 
            if request.data["tag_location_call"]:
                 request.data["tag_location_call"]=Location.objects.get(name)             
        except KeyError:
            request.data['content'] = []
            request.data['tag_user_call'] = []
            request.data["tag_body_call"]=[]
            request.data["tag_location_call"]=[]

        return super().create(request)

    @login_required_ajax
    def create_comment(self, request,pk):
        """Create Post comment.
        Needs `AddC` permission for each body to be associated."""

        # Prevent posts without any community
        if 'community_id' not in request.data or not request.data['community_id']:
            return forbidden_no_privileges()
        parent = self.get_community_post(pk)
        try:
            request.data["status"]=0
            
            request.data["parent"]=parent
            request.data["thread_rank"]=parent.thread_rank +1
            request.data["content"]
            if request.data["tag_user_call"]:
                 request.data["tag_user_call"]=UserProfile.objects.get(name)                
            if request.data["tag_body_call"]:
                 request.data["tag_body_call"]=Body.objects.get(name) 
            if request.data["tag_location_call"]:
                 request.data["tag_location_call"]=Location.objects.get(name)             
        except KeyError:
            request.data['content'] = []
            request.data['tag_user_call'] = []
            request.data["tag_body_call"]=[]
            request.data["tag_location_call"]=[]

        return super().create(request)
        
    @login_required_ajax
    def update_post(self, request, pk):
        """Update Posts.
        Needs BodyRole with `AddP` for at least one associated community.
        Disassociating bodies from the event requires the `DelP`
        permission and associating needs `ModP`"""

        # Prevent events without any body
        if 'community_id' not in request.data or not request.data['community_id']:
            return forbidden_no_privileges()

        # Get the event currently in database
        post = self.get_community_post(pk)

        # Check if difference in bodies is valid
        if not can_update_communities(request.data['community_id'], post, request.user.profile):
            return forbidden_no_privileges()

        try:
            request.data["content"]
            if request.data["tag_user_call"]:
                 request.data["tag_user_call"]=UserProfile.objects.get(name)                
            if request.data["tag_body_call"]:
                 request.data["tag_body_call"]=Body.objects.get(name) 
            if request.data["tag_location_call"]:
                 request.data["tag_location_call"]=Location.objects.get(name) 
        except KeyError:
            request.data['content'] = []
            request.data['tag_user_call'] = []
            request.data["tag_body_call"]=[]
            request.data["tag_location_call"]=[]
        return super().update(request, pk)

    @login_required_ajax
    def update_comment(self, request,pk1,pk2):
        """Create Post comment.
        Needs `AddC` permission for each body to be associated."""

        # Prevent posts without any community
        if 'community_id' not in request.data or not request.data['community_id']:
            return forbidden_no_privileges()
        parent = self.get_community_post(pk1)
        comment = self.get_community_post_comment(pk2)

        if not can_update_communities(request.data['community_id'], comment, request.user.profile):
            return forbidden_no_privileges()
        
        try:
            request.data["status"]=0
            
            request.data["parent"]=parent
            request.data["thread_rank"]=parent.thread_rank +1
            request.data["content"]
            if request.data["tag_user_call"]:
                 request.data["tag_user_call"]=UserProfile.objects.get(name)                
            if request.data["tag_body_call"]:
                 request.data["tag_body_call"]=Body.objects.get(name) 
            if request.data["tag_location_call"]:
                 request.data["tag_location_call"]=Location.objects.get(name)             
        except KeyError:
            request.data['content'] = []
            request.data['tag_user_call'] = []
            request.data["tag_body_call"]=[]
            request.data["tag_location_call"]=[]

        return super().create(request,pk1,pk2)
    
    @login_required_ajax
    def destroy(self, request, pk):
        """Delete Posts.
        Needs `DelP` permission for all associated bodies."""

        post = self.get_community_post(pk)
        if all([user_has_privilege(request.user.profile, str(community.id), 'DelP')
                for community in post.community.all()]):
            return super().destroy(request, pk)

        return forbidden_no_privileges()

    def get_community_post(self, pk):
        """Get a community post from pk uuid or strid."""
        try:
            UUID(pk, version=4)
            return get_object_or_404(self.queryset, id=pk)
        except ValueError:
            return get_object_or_404(self.queryset, str_id=pk)

    def get_community_post_comment(self, pk):
        """Get a community post comment from pk uuid or strid."""
        try:
            UUID(pk, version=4)
            return get_object_or_404(self.queryset, id=pk)
        except ValueError:
            return get_object_or_404(self.queryset, str_id=pk)


def can_update_communities(new_bodies_id, event, profile):
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
        body = self.get_community(pk)

        # Serialize the body
        serialized = CommunitySerializers(body, context={'request': request}).data
        return Response(serialized)

    def get_community(self, pk):
        try:
            UUID(pk, version=4)
            return get_object_or_404(self.queryset, id=pk)
        except ValueError:
            return get_object_or_404(self.queryset, str_id=pk)

    @login_required_ajax
    def join(self,request,pk):
        if request.data["join_community"] and self.get_community(pk):
            user =request.user.profile
            user.followed_communities.append(self.get_community(pk).name)
            self.get_community(pk).followers+=1
