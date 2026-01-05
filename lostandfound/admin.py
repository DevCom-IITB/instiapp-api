from django import forms
from django.contrib import admin
from django.http.response import HttpResponse
from django.utils.html import format_html

from lostandfound.models import ProductFound
from users.models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ["ldap_id", "name", "roll_no"]
    list_display = ["ldap_id", "name", "roll_no"]

    def change_view(
        self, request, object_id, form_url="", extra_context=None
    ) -> HttpResponse:
        class CustomChangeForm(forms.ModelForm):
            """Modify the change form to only show the required fields."""

            class Meta:
                model = UserProfile
                fields = ["ldap_id", "name", "roll_no"]

        self.form = CustomChangeForm
        return super().change_view(request, object_id, form_url, extra_context)


class ProductFoundAdmin(admin.ModelAdmin):
    list_display = ["name", "product_image_display", "category", "found_at", "claimed"]
    search_fields = [
        "name",
        "description",
        "category",
        "found_at",
        "claimed",
        "contact_details",
        "time_of_creation",
        "claimed_by",
    ]

    autocomplete_fields = ["claimed_by"]
    # inlines = [UserProfileInline]

    def product_image_display(self, obj):
        try:
            images = obj.product_image.split(",")
        except AttributeError:
            images = ['']
        return format_html(
            '<div style = "width :200px margin-left:50px"><img src="{}"style="max-height: 150px; /></div>'.format(
                images[0]
            )
        )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # self.inlines = [ImageInline]
        class CustomChangeForm(forms.ModelForm):
            class Meta:
                model = ProductFound
                fields = [
                    "name",
                    "description",
                    "category",
                    "found_at",
                    "claimed",
                    "contact_details",
                    "claimed_by",
                    "product_image1",
                    "product_image2",
                    "product_image3",
                ]

        self.form = CustomChangeForm
        return super().change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        # pylint: disable=useless-super-delegation
        super().save_model(request, obj, form, change)


class CSOAdminSite(admin.AdminSite):
    site_header = "CSO Admin"
    site_title = "CSO Admin Portal"
    index_title = "Welcome to CSO Admin Portal"


cso_admin_site = CSOAdminSite(name="CSOAdmin")
cso_admin_site.register(ProductFound, ProductFoundAdmin)
cso_admin_site.register(UserProfile, UserProfileAdmin)
admin.site.register(ProductFound, ProductFoundAdmin)
