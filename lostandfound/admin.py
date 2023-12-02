from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils.html import format_html
# Register your models here.
import logging
from lostandfound.models import ProductFound
from upload.models import UploadedImage
from django import forms
from users.models import UserProfile

# class ImageInline(admin.TabularInline):
#     model = UploadedImage
# class UserProfileInline(admin.StackedInline):
#     model = UserProfile
#     can_delete = False

class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['ldap_id', 'name', 'roll_no']
    list_display = ['ldap_id', 'name', 'roll_no']

    def change_view(self, request, object_id, form_url='', extra_context=None) -> HttpResponse:
        class CustomChangeForm(forms.ModelForm):
            """ Modify the change form to only show the required fields."""
            class Meta:
                model = UserProfile
                fields = ['ldap_id', 'name', 'roll_no']
        self.form = CustomChangeForm
        return super().change_view(request, object_id, form_url, extra_context)


class ProductFoundAdmin(admin.ModelAdmin):
    list_display = ['name',  'product_image_display', 'category', 'found_at', 
                    'claimed']
    search_fields = ['name', 'description', 'category', 'found_at',
                    'claimed', 'contact_details', 'time_of_creation', 'claimed_by']
    
    autocomplete_fields = ['claimed_by']
    # inlines = [UserProfileInline] 

    def product_image_display(self, obj):
        images = obj.product_image.split(',')
        return format_html('<div style = "width :200px margin-left:50px"><img src="{}"style="max-height: 150px; /></div>'.format(images[0]))
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # self.inlines = [ImageInline]
        class CustomChangeForm(forms.ModelForm):
            class Meta:
                model = ProductFound
                fields = '__all__'


            new_images = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
            names = forms.CharField(required=True)
        self.form = CustomChangeForm
        return super().change_view(request, object_id, form_url, extra_context)
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


       


class CSOAdminSite(admin.AdminSite):
    site_header = "CSO Admin"
    site_title = "CSO Admin Portal"
    index_title = "Welcome to CSO Admin Portal"

    # def has_permission(self, request: HttpRequest):
    #     user_has_permission = request.user.is_active and request.user.is_staff
    #     logging.debug(f'User: {request.user}, Has Permission: {user_has_permission}')
    #     print(f'User: {request.user}, Has Permission: {user_has_permission}')
    #     return user_has_permission

cso_admin_site = CSOAdminSite(name='CSOAdmin')
cso_admin_site.register(ProductFound, ProductFoundAdmin)
cso_admin_site.register(UserProfile, UserProfileAdmin)
admin.site.register(ProductFound, ProductFoundAdmin)