"""Views for venter."""
from rest_framework.generics import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from roles.helpers import login_required_ajax

from venter.models import Complaints
from venter.models import Comment
from venter.models import ComplaintMedia
from venter.models import TagUris

from venter.serializers import ComplaintSerializer
from venter.serializers import ComplaintPostSerializer
from venter.serializers import CommentPostSerializer
from venter.serializers import CommentSerializer

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaints.objects.all()
    serializer_class = ComplaintPostSerializer

    def retrieve(self, request, pk):
        complaint = self.get_complaint(pk)
        serialized = ComplaintSerializer(
            complaint, context={'request': request}).data
        return Response(serialized)

    @classmethod
    def list(cls, request):
        """Get a list of non-deleted complaints.
        To filter by current user, add a query parameter {?filter}"""

        # Get the list of complaints excluding objects marked deleted
        complaint = Complaints.objects.exclude(status='Deleted')

        # Check if the user specific filter is present
        if 'filter' in request.GET:
            complaint = complaint.filter(created_by=request.user.profile)

        # Serialize and return
        serialized = ComplaintSerializer(
            complaint, context={'request': request}, many=True).data
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
                if TagUris.objects.filter(tag_uri=tag).exists():
                    exist_tag = TagUris.objects.get(tag_uri=tag)
                    complaint.tags.add(exist_tag.id)
                else:
                    tag_name = TagUris(tag_uri=tag)
                    tag_name.save()
                    complaint.tags.add(tag_name)

            # Create and save all images if present
            for image in images:
                ComplaintMedia.objects.create(
                    complaint=complaint, image_url=image
                )

        # Return new serialized response
        return Response(ComplaintSerializer(
            Complaints.objects.get(id=complaint.id)
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
            Complaints.objects.get(id=complaint.id)
        ).data, status=200)

    def get_complaint(self, pk):
        """Shortcut for get_object_or_404 with pk"""
        return get_object_or_404(self.queryset, id=pk)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentPostSerializer

    @classmethod
    @login_required_ajax
    def create(cls, request, pk):
        get_complaint = get_object_or_404(Complaints.objects.all(), id=pk)
        get_text = request.data['text']
        comment = Comment.objects.create(text=get_text, commented_by=request.user.profile,
                                         complaint=get_complaint)
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
            Comment.objects.filter(id=pk).update(text=text)
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
