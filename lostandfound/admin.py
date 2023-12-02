from django.contrib import admin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils.html import format_html
# Register your models here.

from lostandfound.models import ProductFound
from upload.models import UploadedImage
from django import forms


# class ImageInline(admin.TabularInline):
#     model = UploadedImage


class ProductFoundAdmin(admin.ModelAdmin):
    list_display = ['name',  'product_image_display', 'category', 'found_at', 
                    'claimed']
    search_fields = ('name', 'description', 'category', 'found_at',
                    'claimed', 'contact_details', 'time_of_creation', 'claimed_by')
    
    # inlines = [ImageInline] 

    def product_image_display(self, obj):
        images = obj.product_image.split(',')
        return format_html('<div style = "width :200px margin-left:50px"><img src="{}"style="max-height: 150px; max-width: 200px; /></div>'.format(images[0]))
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # self.inlines = [ImageInline]


        class CustomChangeForm(forms.ModelForm):
            class Meta:
                model = ProductFound
                fields = '__all__'

            # new_images = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))

        self.form = CustomChangeForm

        return super().change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):

        super().save_model(request, obj, form, change)


        # for new_image in request.FILES.getlist('new_images'):
        #     image_instance = UploadedImage.objects.create(image=new_image, uploaded_by=request.user)
        #     image_instance.save()
        #     obj.product_image += ',' + image_instance.image.url if obj.product_image else image_instance.image.url
        #     obj.save()




class CSOAdminSite(admin.AdminSite):
    site_header = "CSO Admin"
    site_title = "CSO Admin Portal"
    index_title = "Welcome to CSO Admin Portal"


cso_admin_site = CSOAdminSite(name='CSOAdmin')
cso_admin_site.register(ProductFound, ProductFoundAdmin)



admin.site.register(ProductFound, ProductFoundAdmin)