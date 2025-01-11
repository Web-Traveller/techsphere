from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from .models import *

# admin.site.register(Group)
admin.site.register(Permission)

admin.site.register(CustomUser)
admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(Competition)
admin.site.register(TeamCompetitionRegistration)
admin.site.register(ContactMessage)