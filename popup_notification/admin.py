from django.contrib import admin
from .models import PopUp
# Register your models here.
@admin.register(PopUp)
class PopUpAdmin(admin.ModelAdmin):
    list_display = [
        'heading',
        'is_active',
        'created_at',
        'updated_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['heading', 'short_description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']