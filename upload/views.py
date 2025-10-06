"""Views for upload app."""
from rest_framework import viewsets
from upload.serializers import UploadedFileSerializer
from upload.models import UploadedFile
from roles.helpers import login_required_ajax
from rest_framework.response import Response
from rest_framework import status


# class UploadViewSet(viewsets.ModelViewSet):
#     """Upload"""

#     queryset = UploadedImage.objects.all()
#     serializer_class = UploadedImageSerializer

#     def get_serializer_context(self):
#         return {"request": self.request}

#     @login_required_ajax
#     def create(self, request):
#         """Upload file."""
#         return super().create(request)

#     @login_required_ajax
#     def destroy(self, request, pk):
#         """Delete file entry."""
#         return super().destroy(request, pk)

class UploadViewSet(viewsets.ModelViewSet):
    """Upload ViewSet with authentication."""

    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    @login_required_ajax
    def create(self, request):
        """Upload file - requires authentication."""
        # Set the uploaded_by field to current user
        # if hasattr(request, 'data') and isinstance(request.data, dict):
        #     request.data['uploaded_by'] = request.user.profile.id
        
        return super().create(request)
    @login_required_ajax
    def destroy(self, request, pk):
        """Delete file entry - requires authentication."""
        # try:
        #     file_obj = self.get_object()
            
        #     # Check if user owns the file or has permission
        #     if file_obj.uploaded_by != request.user.profile:
        #         return Response(
        #             {'error': 'Permission denied. You can only delete your own files.'}, 
        #             status=status.HTTP_403_FORBIDDEN
        #         )
            
        return super().destroy(request, pk)
            
        # except UploadedImage.DoesNotExist:
        #     return Response(
        #         {'error': 'File not found'}, 
        #         status=status.HTTP_404_NOT_FOUND
        #     )
