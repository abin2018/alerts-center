from django.contrib import admin
from .models import OnCallRole
from .models import OnCallStuff


@admin.register(OnCallRole)
class OnCallRoleAdmin(admin.ModelAdmin):
    list_display = ("role_name", "role_desc", "create_time", "update_time")


@admin.register(OnCallStuff)
class OnCallStuffAdmin(admin.ModelAdmin):
    list_display = ("stuff_name", "on_call_role", "stuff_phone_number", "stuff_email", "create_time", "update_time")
