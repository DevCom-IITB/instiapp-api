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
from community.serializer_min import CommunitySerializerMin, CommunityPostSerializerMin
from community.serializers import CommunitySerializers, CommunityPostSerializers
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

    def hidden_posts(self, request):
        queryset = CommunityPost.objects.filter(hidden=True)
        serializer = CommunityPostSerializerMin(queryset, many=True, context={'request': request})
        data = serializer.data
        return Response({'data': data})

    def pending_posts(self, request):
        queryset = CommunityPost.objects.filter(status=0)
        print(queryset)
        serializer = CommunityPostSerializerMin(queryset, many=True, context={'request': request})
        print(serializer)
        data = serializer.data
        return Response({'data': data})

    def reported_content(self, request):
        queryset = CommunityPost.objects.filter(reported=True)
        serializer = CommunityPostSerializerMin(queryset, many=True, context={'request': request})
        data = serializer.data
        return Response({'data': data})

    def feature_posts(self,request,pk):
        '''action==1 for featuring a post'''
        if all([user_has_privilege(request.user.profile, id, 'FeaP')]):
            post = self.get_community_post(pk)
            if 'community_id' not in request.data or not request.data['community_id']:
                return forbidden_no_privileges()
            # Get query param
            value = request.GET.get("action")
            if value is None:
                return Response({"message": "{?action} is required"}, status=400)

            # Check possible actions
            if value == "1":
                post.featured = True
            return super().update(post, pk)

    def moderate_comment(self, request, pk):
        if all([user_has_privilege(request.user.profile, id, 'ModC')]):
            post = self.get_community_post(pk)
            if 'community_id' not in request.data or not request.data['community_id']:
                return forbidden_no_privileges()
            # Get query param
            value = request.GET.get("action")
            if value is None:
                return Response({"message": "{?action} is required"}, status=400)

            # Check possible actions
            if value == "0" and post.thread_rank > 1:
                post.hidden = True
            return super().update(post, pk)

    def approval(self, request, pk):
        if all([user_has_privilege(request.user.profile, id, 'AppP')]):
            post = self.get_community_post(pk)
            if 'community_id' not in request.data or not request.data['community_id']:
                return forbidden_no_privileges()
            # Get query param
            value = request.GET.get("action")
            if value is None:
                return Response({"message": "{?action} is required"}, status=400)

            # Check possible actions
            if value == "0" and post.thread_rank == 1:
                post.status = 2
            elif value == "1" and post.thread_rank == 1:
                post.status = 1
            return super().update(post, pk)
    def pending_posts(self, request):
        queryset = CommunityPost.objects.filter(status=0)
        serializer = CommunityPostSerializerMin(queryset, many=True, context={'request': request})
        data = serializer.data
        return Response({'data': data})



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

        queryset = CommunityPost.objects.filter(status=1, thread_rank=1).order_by("-time_of_modification")
        queryset = query_search(request, 3, queryset, ['content'], 'posts')
        queryset = query_from_num(request, 20, queryset)

        serializer = CommunityPostSerializerMin(queryset, many=True, context={'request': request})
        data = serializer.data

        return Response({'count': len(data), 'data': data})

    @login_required_ajax
    def create(self, request):
        """Create Post and Comments.
        Needs `AddP` permission for each body to be associated."""
        # Prevent posts without any community
        if 'community' not in request.data or not request.data['community']:
            return forbidden_no_privileges()
        user = request.user.profile
        try:
            request.data["parent"]
            request.data["content"]
            # request.data["tag_user_call"]
            # request.data["tag_body_call"]
            # request.data["tag_location_call"]
        except KeyError:
            request.data['content'] = []
            request.data['parent'] = []
            # request.data['tag_user_call'] = []
            # request.data["tag_body_call"] = []
            # request.data["tag_location_call"] = []

        return super().create(request)

    @login_required_ajax
    def update(self, request, *args, **kwargs):
        """Update Posts and comments.
        Needs BodyRole with `AddP` for at least one associated community.
        Disassociating bodies from the event requires the `DelP`
        permission and associating needs `ModP`"""
        pk = self.kwargs.get('pk')

        # Prevent events without any body
        if 'community_id' not in request.data or not request.data['community_id']:
            return forbidden_no_privileges()

        # Get the event currently in database
        post = self.get_community_post(pk)

        # Check if difference in bodies is valid

        try:
            post.content = request.data["content"]
            post.tag_user = request.data["tag_user_call"]
            post.tag_body = request.data["tag_body_call"]
            post.tag_location = request.data["tag_location_call"]
        except KeyError:
            request.data['content'] = []
            request.data['tag_user_call'] = []
            request.data["tag_body_call"] = []
            request.data["tag_location_call"] = []
        return super().update(post, pk)

    @login_required_ajax
    def destroy(self, request, *args, **kwargs):
        """Delete Posts and comments.
        Needs `DelP` permission for all associated bodies."""
        pk = self.kwargs.get('pk')

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

class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects
    serializer_class = CommunitySerializers

    def get_serializer_context(self):
        return super().get_serializer_context()

    def list(self, request):
        queryset = Community.objects.all()
        queryset = query_search(request, 3, queryset, ['name'], 'communities')
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
    def join(self, request, pk):
        """Join or Unjoin a community {?action}=0,1"""

        body = self.get_community(pk).body

        # Get query param
        value = request.GET.get("action")
        if value is None:
            return Response({"message": "{?action} is required"}, status=400)

        # Check possible actions
        if value == "0":
            request.user.profile.followed_bodies.remove(body)
        elif value == "1":
            request.user.profile.followed_bodies.add(body)
        else:
            return Response({"message": "Invalid Action"}, status=400)

        return Response(status=204)
