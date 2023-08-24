from django.contrib import admin
from .models import userProfile, Project, Bug
# Register your models here.

admin.site.register(userProfile)
admin.site.register(Project)
admin.site.register(Bug)