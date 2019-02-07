from django.contrib import admin
from upload.models import UploadedImage

class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('uploaded_by', 'is_claimed', 'claimant')
    raw_id_fields = ('uploaded_by',)


admin.site.register(UploadedImage, UploadedImageAdmin)
