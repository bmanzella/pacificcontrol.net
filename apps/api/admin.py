from django.contrib import admin
from .models import Controller, ControllerSession


@admin.register(Controller)
class ControllerAdmin(admin.ModelAdmin):
    list_display = ('user', 'callsign', 'online_since', 'last_update', 'duration')


@admin.register(ControllerSession)
class ControllerSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'callsign', 'start', 'duration')
