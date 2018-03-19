"""Views for upload app."""
from rest_framework import viewsets
from upload.serializers import UploadedImageSerializer
from upload.models import UploadedImage
from roles.helpers import login_required_ajax

class UploadViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that allows files to be uploaded."""
    queryset = UploadedImage.objects.all()
    serializer_class = UploadedImageSerializer

    @login_required_ajax
    def create(self, request):
        """Upload an image."""
        return super().create(request)

    @login_required_ajax
    def destroy(self, request, pk):
        """Delete an image entry."""
        return super().destroy(request, pk)
