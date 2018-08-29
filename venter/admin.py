from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from .models import complaints
from .models import comment
from .models import complaints_liked_users
from .models import tag_uris
from .models import complaint_tag_uris
from .models import media_uris


class CommentTabularInline(admin.TabularInline):
    model = comment


class ComplaintsLikedUsersTabularInline(admin.TabularInline):
    model = complaints_liked_users


class ComplaintTagUrisTabularInline(admin.TabularInline):
    model = complaint_tag_uris


class MediaUrisTabularInline(admin.TabularInline):
    model = media_uris


class CommentModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "complaint", "time"]
    model = comment


class ComplaintTagUriModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "complaint"]
    model = complaint_tag_uris


class ComplaintLikedUsersModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "complaint"]
    model = complaints_liked_users


class MediaUriModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "complaint"]
    model = media_uris


class ComplaintModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "report_date", "status"]
    list_editable = ["status"]
    list_filter = ["status"]
    inlines = [CommentTabularInline, ComplaintsLikedUsersTabularInline, ComplaintTagUrisTabularInline,
               MediaUrisTabularInline]
    search_fields = [ "status", "description", "user__name"]

    class Meta:
        model = complaints


admin.site.register(complaints, ComplaintModelAdmin)
admin.site.register(complaint_tag_uris, ComplaintTagUriModelAdmin)
admin.site.register(media_uris, MediaUriModelAdmin)
admin.site.register(comment, CommentModelAdmin)
admin.site.register(complaints_liked_users, ComplaintLikedUsersModelAdmin)
admin.site.register(tag_uris)
