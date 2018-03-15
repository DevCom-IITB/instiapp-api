"""Views for upload app."""
from rest_framework import viewsets
from upload.serializers import UploadedImageSerializer
from upload.models import UploadedImage

class UploadViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that allows files to be uploaded."""
    queryset = UploadedImage.objects.all()
    serializer_class = UploadedImageSerializer
