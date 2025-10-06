from uuid import UUID
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from community.models import Community
from community.models import CommunityPost
from community.models import Poll, PollOption, PollVote
from community.serializer_min import CommunitySerializerMin, CommunityPostSerializerMin
from community.serializers import CommunitySerializers, CommunityPostSerializers, PollSerializer, PollOptionSerializer 
from roles.helpers import user_has_privilege
from roles.helpers import login_required_ajax
from roles.helpers import forbidden_no_privileges
from helpers.misc import query_from_num
from helpers.misc import query_search
from users.models import UserProfile
from rest_framework import status
from django.db import transaction


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

        if (
            user_has_privilege(request.user.profile, post.community.body.id, "AppP")
            and post.thread_rank == 1
        ) or (
            user_has_privilege(request.user.profile, post.community.body.id, "ModC")
            and post.thread_rank > 1
        ):
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
        return {"request": self.request}

    @login_required_ajax
    def retrieve_full(self, request, pk):
        """Get full Post.
        Get by `uuid` or `str_id`"""

        self.queryset = CommunityPostSerializers.setup_eager_loading(
            self.queryset, request
        )
        post = self.get_community_post(pk)
        return_for_mod = False
        if user_has_privilege(request.user.profile, post.community.body.id, "AppP"):
            return_for_mod = True
        serialized = CommunityPostSerializers(
            post, context={"return_for_mod": return_for_mod}
        ).data

        return Response(serialized)

    @login_required_ajax
    def list(self, request):
        """List Of Posts.
        List fresh posts arranged chronologiaclly for the current user."""

        # Check for time and date filtered query params
        status = request.GET.get("status")
        comm_id = request.GET.get("community")
        if comm_id is None:
            return Response({"message": "comm_id is required"}, status=400)
        community = get_object_or_404(Community.objects, id=comm_id)

        # If your posts
        if status is None:
            queryset = CommunityPost.objects.filter(
                thread_rank=1, community=community, posted_by=request.user.profile
            ).order_by("-time_of_modification")
        else:
            # If reported posts
            if status == "3":
                queryset = CommunityPost.objects.filter(
                    status=status, community=community, deleted=False
                ).order_by("-time_of_modification")
                # queryset = CommunityPost.objects.all()

            else:
                queryset = CommunityPost.objects.filter(
                    status=status, community=community, deleted=False, thread_rank=1
                ).order_by("-time_of_modification")
        queryset = query_search(request, 3, queryset, ["content"], "posts")
        queryset = query_from_num(request, 20, queryset)
        return_for_mod = False
        if user_has_privilege(request.user.profile, community.body.id, "AppP"):
            return_for_mod = True

        serializer = CommunityPostSerializerMin(
            queryset, many=True, context={"return_for_mod": return_for_mod}
        )
        data = serializer.data

        return Response({"count": len(data), "data": data})

    @login_required_ajax
    def create(self, request):
        """Create Post and Comments.
        Needs `AddP` permission for each body to be associated."""
        # Prevent posts without any community
        if "community" not in request.data or not request.data["community"]:
            return forbidden_no_privileges()
        
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # user, created = UserProfile.objects.get_or_create(user=request.user)

        # response = super().create(request)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @login_required_ajax
    def vote_on_poll(self, request, pk):
        try:
            community_post = self.get_community_post(pk)
            poll = get_object_or_404(Poll, id=community_post.poll.id)
            user = request.user.profile
            option_ids = request.data.get('options', [])

            with transaction.atomic():
                if poll.allow_multiple_answers:
                    # --- Handle Multiple-Choice ---
                    if not option_ids:
                        PollVote.objects.filter(poll=poll, user=user).delete()
                        message = "All votes removed"
                    else:
                        valid_options = list(PollOption.objects.filter(id__in=option_ids, poll=poll))
                        if len(valid_options) != len(option_ids):
                            return Response({"error": "One or more option IDs are invalid."}, status=status.HTTP_400_BAD_REQUEST)
                        
                        PollVote.objects.filter(poll=poll, user=user).delete()
                        new_votes = [PollVote(poll=poll, option=option, user=user) for option in valid_options]
                        PollVote.objects.bulk_create(new_votes)
                        message = f"Voted for {len(valid_options)} options"
                else:
                    # --- Handle Single-Choice ---
                    if not option_ids:
                        PollVote.objects.filter(poll=poll, user=user).delete()
                        message = "Vote removed"
                    else:
                        if len(option_ids) > 1:
                            return Response({"error": "Only one option is allowed."}, status=status.HTTP_400_BAD_REQUEST)
                        
                        option = get_object_or_404(PollOption, id=option_ids[0], poll=poll)
                        deleted_count, _ = PollVote.objects.filter(poll=poll, user=user, option=option).delete()

                        if deleted_count > 0:
                            message = "Vote removed"
                        else:
                            PollVote.objects.filter(poll=poll, user=user).delete()
                            PollVote.objects.create(poll=poll, option=option, user=user)
                            message = "Vote updated"
            
            # Return the full, updated poll data
            poll_serializer = PollSerializer(poll, context={'request': request})
            return Response({"message": message, "poll": poll_serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in vote_on_poll: {e}") # Good for debugging
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
        """action==feature for featuring a post"""
        post = self.get_community_post(pk)

        if action == "feature":
            if all(
                [
                    user_has_privilege(
                        request.user.profile, post.community.body.id, "AppP"
                    )
                ]
            ):
                # Get query param
                is_featured = request.data["is_featured"]
                if is_featured is None:
                    return Response(
                        {"message": "{?is_featured} is required"}, status=400
                    )

                # Check possible actions

                post.featured = is_featured
                post.save()
                return Response(
                    {"message": "is_featured changed", "is_featured": is_featured}
                )

            return forbidden_no_privileges()

        if action == "delete":
            if request.user.profile == post.posted_by:
                post.deleted = True
                post.featured = False
                post.save()
                return Response({"message": "Post deleted"})

            if all(
                [
                    user_has_privilege(
                        request.user.profile, post.community.body.id, "AppP"
                    )
                ]
            ):
                post.status = 2
                post.featured = False
                post.save()
                return Response({"message": "Post deleted"})

            return forbidden_no_privileges()

        if action == "report":
            if request.user.profile not in post.reported_by.all():
                post.reported_by.add(request.user.profile)
                # post.reports +=1
                post.save()
                return Response({"message": "Post reported"})
            post.reported_by.remove(request.user.profile)
            # post.reports -=1
            post.save()
            return Response({"message": "Post unreported"})
        if action == "vote":
            return self._vote_on_poll(request, post)

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

    @login_required_ajax
    def list(self, request):
        queryset = Community.objects.all()
        queryset = query_search(
            request, 3, queryset, ["name", "about", "description"], "communities"
        )
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
        serialized = CommunitySerializers(body, context={"request": request}).data
        return Response(serialized)

    def get_community(self, pk):
        try:
            UUID(pk, version=4)
            return get_object_or_404(self.queryset, id=pk)
        except ValueError:
            return get_object_or_404(self.queryset, str_id=pk)

    @login_required_ajax
    def create(self, request):
        name = request.data["name"]
        user, created = UserProfile.objects.get_or_create(user=request.user)
        if not Community.objects.all().filter(name=name).exists():
            super().create(request)
            return Response({"message": "Community created"})

        return Response({"message": "Community already exists"}, status=400)

    # @login_required_ajax
    # def _vote_on_poll(self, request, post):
    #     """Vote on a poll option"""
    #     try:
    #         if not hasattr(post, 'poll'):
    #             return Response({'error': 'This post is not a poll'}, status=400)
    #         poll = Poll.objects.get(id=poll_id)
    #         option_ids = request.data.get('option_ids', [])
            
    #         if not option_ids:
    #             return Response({'error': 'No options selected'}, status=400)
            
    #         # Remove existing votes if single answer poll
    #         if not poll.allow_multiple_answers:
    #             PollVote.objects.filter(poll=poll, user=request.user.profile).delete()
            
    #         # Create new votes
    #         for option_id in option_ids:
    #             option = PollOption.objects.get(id=option_id, poll=poll)
    #             PollVote.objects.get_or_create(
    #                 poll=poll,
    #                 option=option,
    #                 user=request.user.profile
    #             )
            
    #         return Response({'message': 'Vote recorded'})
            
    #     except Poll.DoesNotExist:
    #         return Response({'error': 'Poll not found'}, status=404)
    #     except PollOption.DoesNotExist:
    #         return Response({'error': 'Invalid poll option'}, status=400)
        
    # def _get_poll_results(self,request, post):
    #     """Get poll results"""
    #     try:
    #         if not hasattr(post, 'poll'):
    #             return Response({'error': 'This post is not a poll'}, status=400)
            
    #         poll = Poll.objects.get(id=poll_id)
    #         total_votes = PollVote.objects.filter(poll=poll).count()
            
    #         results = []
    #         for option in poll.options.all():
    #             vote_count = PollVote.objects.filter(option=option).count()
    #             percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
    #             results.append({
    #                 'id': str(option.id),
    #                 'text': option.text,
    #                 'vote_count': vote_count,
    #                 'percentage': round(percentage, 1)
    #             })
            
    #         return Response({
    #             'total_votes': total_votes,
    #             'options': results
    #         })
    #     except Poll.DoesNotExist:
    #         return Response({'error': 'Poll not found'}, status=404)