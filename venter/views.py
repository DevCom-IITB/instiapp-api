from rest_framework.generics import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from roles.helpers import login_required_ajax
from venter.models import Complaints, Comment, ComplaintMedia, TagUris
from venter.serializers import ComplaintSerializer, ComplaintPostSerializer, CommentPostSerializer, CommentSerializer


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
        complaint = Complaints.objects.all()
        if 'filter' in request.GET:
            complaint = complaint.filter(created_by=request.user.profile)
        serialized = ComplaintSerializer(
            complaint, context={'request': request}, many=True).data
        return Response(serialized)

    @login_required_ajax
    def create(self, request):
        images = request.data['images']
        tags = request.data['tags']
        serializer = ComplaintPostSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            complaint = serializer.save()
            if tags:
                for tag in tags:
                    if TagUris.objects.filter(tag_uri=tag).exists():
                        exist_tag = TagUris.objects.get(tag_uri=tag)
                        complaint.tags.add(exist_tag.id)
                    else:
                        tag_name = TagUris(tag_uri=tag)
                        tag_name.save()
                        complaint.tags.add(tag_name)
            if images:
                for image in images:
                    ComplaintMedia.objects.create(
                        complaint=complaint, image_url=image
                    )
        return Response(ComplaintSerializer(
            Complaints.objects.get(id=complaint.id)
        ).data, status=201)

    def get_complaint(self, pk):
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
        text = request.data['text']
        comment = self.get_comment(pk)
        if comment.commented_by == self.request.user.profile:
            Comment.objects.filter(id=pk).update(text=text)
            serialized = CommentPostSerializer(self.get_comment(pk), context={'request': request}).data
            return Response(serialized)
        return Response(status=403)

    @login_required_ajax
    def destroy(self, request, pk):
        comment = self.get_comment(pk)
        if comment.commented_by == self.request.user.profile:
            return super().destroy(request, pk)
        else:
            return Response(status=403)

    @login_required_ajax
    def retrieve(self, request, pk):
        comment = self.get_comment(pk)
        serialized = CommentSerializer(comment, context={'request': request}).data
        return Response(serialized)

    def get_comment(self, pk):
        return get_object_or_404(self.queryset, id=pk)
