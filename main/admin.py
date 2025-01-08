# main/admin.py
from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(Competition)  # Register your Competition model here
admin.site.register(TeamCompetitionRegistration)
admin.site.register(ContactMessage)