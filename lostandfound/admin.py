from django.contrib import admin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils.html import format_html
# Register your models here.

from lostandfound.models import ProductFound

class ProductFoundAdmin(admin.ModelAdmin):
    list_display = ['name',  'product_image_display', 'category', 'found_at', 
                    'claimed']
    search_fields = ('name', 'description', 'product_image', 'category', 'found_at',
                    'claimed', 'contact_details', 'time_of_creation', 'claimed_by')
    
    def product_image_display(self, obj):
        images = obj.product_image.split(',')
        return format_html('<img src="{}"style="max-height: 150px; max-width: 150px; />'.format(images[0]))
    
    def change_view(self, request: HttpRequest, object_id: str, form_url: str = ..., extra_context: dict[str, bool] | None = ...) -> HttpResponse:
        original_change_view = super().change_view(request, object_id, form_url, extra_context)
        
    


admin.site.register(ProductFound, ProductFoundAdmin)