from uuid import UUID
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from community.models import Community
from community.models import CommunityPost
from community.serializer_min import CommunitySerializerMin, CommunityPostSerializerMin
from community.serializers import CommunitySerializers, CommunityPostSerializers
from roles.helpers import user_has_privilege
from roles.helpers import login_required_ajax
from roles.helpers import forbidden_no_privileges
from helpers.misc import query_from_num
from helpers.misc import query_search

class ModeratorViewSet(viewsets.ModelViewSet):
    queryset = CommunityPost.objects
    serializer_class = CommunityPostSerializers
    serializer_class_min = CommunityPostSerializerMin

    def get_community_post(self, pk):
        """Get a community post from pk uuid or strid."""
        try:
            UUID(pk, version=4)
            return get_object_or_404(self.queryset, id=pk)
        except ValueError:
            return get_object_or_404(self.queryset, str_id=pk)

    def change_status(self, request, pk):
        post = self.get_community_post(pk)

        if ((user_has_privilege(request.user.profile, post.community.body.id, 'AppP') and post.thread_rank == 1)
                or (user_has_privilege(request.user.profile, post.community.body.id, 'ModC') and post.thread_rank > 1)):
            # Get query param
            status = request.data["status"]
            if status is None:
                return Response({"message": "{?action} is required"}, status=400)
            if post.status == 3:
                post.ignored = True

            # Check possible actions
            post.status = status
            post.save()
            return Response({"message": "Status changed"})

        return forbidden_no_privileges()


class PostViewSet(viewsets.ModelViewSet):
    """Post"""

    queryset = CommunityPost.objects
    serializer_class = CommunityPostSerializers
    serializer_class_min = CommunityPostSerializerMin

    def get_serializer_context(self):
        return {'request': self.request}

    @login_required_ajax
    def retrieve_full(self, request, pk):
        """Get full Post.
        Get by `uuid` or `str_id`"""

        self.queryset = CommunityPostSerializers.setup_eager_loading(self.queryset, request)
        post = self.get_community_post(pk)
        serialized = CommunityPostSerializers(post, context={'request': request}).data

        return Response(serialized)

    @login_required_ajax
    def list(self, request):
        """List Of Posts.
        List fresh posts arranged chronologiaclly for the current user."""

        # Check for time and date filtered query params
        status = request.GET.get("status")

        # If your posts
        if status is None:
            queryset = CommunityPost.objects.filter(thread_rank=1, posted_by=request.user
                                                    .profile).order_by("-time_of_modification")
        else:
            # If reported posts
            if status == "3":
                queryset = CommunityPost.objects.filter(status=status, deleted=False).order_by("-time_of_modification")
                # queryset = CommunityPost.objects.all()

            else:
                queryset = CommunityPost.objects.filter(
                    status=status, deleted=False, thread_rank=1).order_by("-time_of_modification")
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

        return super().create(request)

    @login_required_ajax
    def update(self, request, pk):
        """Update Event.
        Needs BodyRole with `UpdE` for at least one associated body.
        Disassociating bodies from the event requires the `DelE`
        permission and associating needs `AddE`"""
        post = self.get_community_post(pk)
        if post.posted_by != request.user.profile:
            return forbidden_no_privileges()

        return super().update(request, pk)

    def perform_action(self, request, action, pk):
        '''action==feature for featuring a post'''
        post = self.get_community_post(pk)

        if (action == "feature"):
            if all([user_has_privilege(request.user.profile, post.community.body.id, 'AppP')]):

                # Get query param
                is_featured = request.data["is_featured"]
                if is_featured is None:
                    return Response({"message": "{?is_featured} is required"}, status=400)

                # Check possible actions

                post.featured = is_featured
                post.save()
                return Response({"message": "is_featured changed", 'is_featured': is_featured})

            return forbidden_no_privileges()

        if (action == "delete"):
            if (request.user.profile == post.posted_by):
                post.deleted = True
                post.featured = False
                post.save()
                return Response({"message": "Post deleted"})

            if all([user_has_privilege(request.user.profile, post.community.body.id, 'AppP')]):
                post.status = 2
                post.featured = False
                post.save()
                return Response({"message": "Post deleted"})

            return forbidden_no_privileges()

        if (action == "report"):
            if (request.user.profile not in post.reported_by.all()):
                post.reported_by.add(request.user.profile)
                # post.reports +=1
                post.save()
                return Response({"message": "Post reported"})
            else:
                post.reported_by.remove(request.user.profile)
                # post.reports -=1
                post.save()
                return Response({"message": "Post unreported"})

        return Response({"message": "action not supported"}, status=400)

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

    @login_required_ajax
    def list(self, request):
        queryset = Community.objects.all()
        queryset = query_search(request, 3, queryset, ['name', 'about', 'description'], 'communities')
        serializer = CommunitySerializerMin(queryset, many=True)
        data = serializer.data
        return Response(data)

    @login_required_ajax
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
