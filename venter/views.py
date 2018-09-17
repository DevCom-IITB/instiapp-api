from uuid import UUID

from roles.helpers import login_required_ajax
from venter.models import Complaints, Comment, ComplaintMedia
from venter.serializers import ComplaintSerializer, ComplaintPostSerializer, CommentPostSerializer, CommentSerializer
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaints.objects.all()
    serializer_class = ComplaintPostSerializer

    def retrieve(self, request, pk):
        complaint = self.get_complaint(pk)
        serialized = ComplaintSerializer(
            complaint, context={'request': request}).data
        return Response(serialized)

    def list(self, request):
        complaint = Complaints.objects.all()
        if 'filter' in request.GET:
            complaint = complaint.filter(created_by=request.user.profile)
        serialized = ComplaintSerializer(
            complaint, context={'request': request}, many=True).data
        return Response(serialized)

    @login_required_ajax
    def create(self, request):
        images = request.data['images']
        serializer = ComplaintPostSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            complaint = serializer.save()
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

    @login_required_ajax
    def create(self, request, pk):
        get_complaint = get_object_or_404(Complaints.objects.all(), id=pk)
        get_text = request.data['text']
        comment = Comment.objects.create(text=get_text, commented_by=request.user.profile,
                                         complaint=get_complaint)
        serialized = CommentSerializer(comment)
        return Response(serialized.data, status=201)

    @login_required_ajax
    def update(self, request, pk):
        text = request.data['text']
        Comment.objects.filter(id=pk).update(text=text)
        get_comment = self.get_comment(pk)
        serialized = CommentPostSerializer(get_comment, context={'request': request}).data
        return Response(serialized)

    @login_required_ajax
    def destroy(self, request, pk):
        # Comment.objects.filter(id=pk).delete()
        # return Response(status=204)
        return super().destroy(request, pk)

    @login_required_ajax
    def retrieve(self, request, pk):
        comment = self.get_comment(pk)
        serialized = CommentSerializer(comment, context={'request': request}).data
        return Response(serialized)

    def get_comment(self, pk):
        return get_object_or_404(self.queryset, id=pk)
