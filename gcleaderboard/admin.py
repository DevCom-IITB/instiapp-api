from django.contrib import admin
from .models import GC, GC_Hostel_Points, Hostel  # Import your GCLeaderboard model


class GCLeaderboardAdmin(admin.ModelAdmin):
    list_display = ("id","name", "type")


class GC_Hostel_PointsAdmin(admin.ModelAdmin):
    list_display = ("id" , "gc", "hostel", "points")


admin.site.register(GC, GCLeaderboardAdmin)
admin.site.register(GC_Hostel_Points, GC_Hostel_PointsAdmin)
