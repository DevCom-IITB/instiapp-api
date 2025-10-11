"""Views for upload app."""
from rest_framework import viewsets
from upload.serializers import UploadedImageSerializer
from upload.models import UploadedImage
from roles.helpers import login_required_ajax


class UploadViewSet(viewsets.ModelViewSet):
    """Upload"""

    queryset = UploadedImage.objects.all()
    serializer_class = UploadedImageSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    @login_required_ajax
    def create(self, request):
        """Upload file."""
        return super().create(request)

    @login_required_ajax
    def destroy(self, request, pk):
        """Delete file entry."""
        return super().destroy(request, pk)
