from django.contrib import admin
from bodies.models import Body, BodyChildRelation

admin.site.register(Body)
admin.site.register(BodyChildRelation)
