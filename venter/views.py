"""Views for venter."""
from functools import reduce
import operator
from django.db.models import Q
from django.conf import settings
from rest_framework.generics import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from helpers.misc import query_from_num
from roles.helpers import login_required_ajax

from venter.models import Complaint
from venter.models import ComplaintComment
from venter.models import ComplaintImage
from venter.models import ComplaintTag

from venter.serializers import ComplaintSerializer
from venter.serializers import TagSerializer
from venter.serializers import ComplaintPostSerializer
from venter.serializers import CommentPostSerializer
from venter.serializers import CommentSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = ComplaintTag.objects
    serializer_class = TagSerializer

    @classmethod
    def list(cls, request):
        """TagViewSet for the getting related tags"""
        queryset = ComplaintTag.objects.all()
        if 'tags' in request.GET:
            val = request.query_params.get('tags')
            queryset = ComplaintTag.objects.filter(tag_uri__icontains=val)

        # Serialize and return
        serialized = TagSerializer(
            queryset, context={'get': 'list'}, many=True).data

        return Response(serialized)


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects
    serializer_class = ComplaintPostSerializer

    def retrieve(self, request, pk):
        """ComplaintViewSet to get the complaints"""
        complaint = self.get_complaint(
            pk, queryset=self.queryset.prefetch_related('subscriptions', 'users_up_voted'))
        serialized = ComplaintSerializer(
            complaint, context={'request': request}).data

        is_sub = request.user.is_authenticated and request.user.profile in complaint.subscriptions.all()
        serialized['is_subscribed'] = is_sub

        upvoted = request.user.is_authenticated and request.user.profile in complaint.users_up_voted.all()
        serialized['upvoted'] = upvoted

        return Response(serialized)

    def list(self, request):
        """Get a list of non-deleted complaints.
        To filter by current user, add a query parameter {?filter}"""

        # Get the list of complaints excluding objects marked deleted
        complaints = self.queryset.prefetch_related(
            'subscriptions', 'users_up_voted').exclude(status='Deleted')

        # Check if the user specific filter is present
        if 'filter' in request.GET and request.user.is_authenticated:
            complaints = complaints.filter(created_by=request.user.profile)

        # Filter for a particular word search
        if 'search' in request.GET:
            val = request.query_params.get('search')
            complaints = complaints.filter(description__icontains=val)

        # For multiple tags and single tags
        if 'tags' in request.GET:
            val = request.query_params.getlist('tags')
            clauses = (Q(tags__tag_uri__icontains=p) for p in val)
            query = reduce(operator.or_, clauses)
            complaints = complaints.filter(query)

        # Paginate the complaint page using the helper function
        complaints = query_from_num(request, 10, complaints)

        # Serialize and return
        serialized = ComplaintSerializer(
            complaints, context={'request': request}, many=True).data

        for complaint_object, serialized_object in zip(complaints, serialized):
            is_sub = request.user.is_authenticated and request.user.profile in complaint_object.subscriptions.all()
            serialized_object['is_subscribed'] = is_sub

            upvoted = request.user.is_authenticated and request.user.profile in complaint_object.users_up_voted.all()
            serialized_object['upvoted'] = upvoted

        return Response(serialized)

    @classmethod
    @login_required_ajax
    def create(cls, request):
        # Check for images and tags
        images = request.data.get('images', [])
        tags = request.data.get('tags', [])

        # Deserialize POST data
        serializer = ComplaintPostSerializer(
            data=request.data, context={'request': request})

        # Save if valid
        if serializer.is_valid():
            complaint = serializer.save()

            # Create and save all tags if present
            for tag in tags:
                if ComplaintTag.objects.filter(tag_uri=tag).exists():
                    exist_tag = ComplaintTag.objects.get(tag_uri=tag)
                    complaint.tags.add(exist_tag.id)
                else:
                    tag_name = ComplaintTag(tag_uri=tag)
                    tag_name.save()
                    complaint.tags.add(tag_name)

            # Create and save all images if present
            for image in images:
                ComplaintImage.objects.create(
                    complaint=complaint, image_url=image
                )
            # Add the complaint creator to the subscribers list
            if settings.COMPLAINT_AUTO_SUBSCRIBE:
                complaint.subscriptions.add(complaint.created_by)
                complaint.save()

        # Return new serialized response
        return Response(ComplaintSerializer(
            Complaint.objects.get(id=complaint.id)
        ).data, status=201)

    @login_required_ajax
    def up_vote(self, request, pk):
        """UpVote or un-UpVote a complaint {?action}=0,1"""

        complaint = self.get_complaint(pk)

        value = request.GET.get("action")
        if value is None:
            return Response({"message": "{?action} is required"}, status=400)

        # Check possible actions
        if value == "0":
            complaint.users_up_voted.remove(self.request.user.profile)
        elif value == "1":
            complaint.users_up_voted.add(self.request.user.profile)
        else:
            return Response({"message": "Invalid Action"}, status=400)

        return Response(ComplaintSerializer(
            Complaint.objects.get(id=complaint.id)
        ).data, status=200)

    @login_required_ajax
    def subscribe(self, request, pk):
        """Subscribe or Un-Subscribe from a complaint {?action}=0,1"""

        complaint = self.get_complaint(pk)

        value = request.GET.get("action")
        if value is None:
            return Response({"message": "{?action} is required"}, status=400)

        # Check possible actions
        if value == "0":
            complaint.subscriptions.remove(self.request.user.profile)
        elif value == "1":
            complaint.subscriptions.add(self.request.user.profile)
        else:
            return Response({"message": "Invalid Action"}, status=400)

        return Response(ComplaintSerializer(
            Complaint.objects.get(id=complaint.id)
        ).data, status=200)

    def get_complaint(self, pk, queryset=None):
        """Shortcut for get_object_or_404 with pk"""
        return get_object_or_404(queryset or self.queryset, id=pk)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = ComplaintComment.objects
    serializer_class = CommentPostSerializer

    @classmethod
    @login_required_ajax
    def create(cls, request, pk):
        get_complaint = get_object_or_404(Complaint.objects.all(), id=pk)
        get_text = request.data['text']
        comment = ComplaintComment.objects.create(
            text=get_text, commented_by=request.user.profile, complaint=get_complaint)
        # Auto subscribes the commenter to the complaint
        if settings.COMPLAINT_AUTO_SUBSCRIBE:
            get_complaint.subscriptions.add(request.user.profile)
            get_complaint.save()

        serialized = CommentSerializer(comment)
        return Response(serialized.data, status=201)

    @login_required_ajax
    def update(self, request, pk):
        """Update a comment if created by current user."""

        # Retrieve the comment and updated text
        text = request.data['text']
        comment = self.get_comment(pk)

        # Check if the comment is done by current user
        if comment.commented_by == self.request.user.profile:
            ComplaintComment.objects.filter(id=pk).update(text=text)
            serialized = CommentPostSerializer(self.get_comment(pk), context={'request': request}).data
            return Response(serialized)

        # If not authorized
        return Response(status=403)

    @login_required_ajax
    def destroy(self, request, pk):
        """Delete a comment by the current user."""
        comment = self.get_comment(pk)
        if comment.commented_by == self.request.user.profile:
            return super().destroy(request, pk)
        return Response(status=403)

    @login_required_ajax
    def retrieve(self, request, pk):
        """Get a single comment."""
        comment = self.get_comment(pk)
        serialized = CommentSerializer(comment, context={'request': request}).data
        return Response(serialized)

    def get_comment(self, pk):
        """Shortcut for get_object_or_404."""
        return get_object_or_404(self.queryset, id=pk)
