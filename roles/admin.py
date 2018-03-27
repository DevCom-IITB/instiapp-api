from django.contrib import admin
from roles.models import BodyRole
from roles.models import InstituteRole

admin.site.register(BodyRole)
admin.site.register(InstituteRole)
