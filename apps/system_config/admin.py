from django.contrib import admin
from .models import SystemConfigure
from .forms import SystemConfigureForm


@admin.register(SystemConfigure)
class SystemConfigureAdmin(admin.ModelAdmin):
    list_display = ("configure_name", "update_on_call_switch","send_on_call_info_switch",
                    "clean_alert_inhibition_expired_switch","unresolved_alerts_reminder_switch")
    fieldsets = (('配置名称', {'fields': ("configure_name",)}),
                 (("定时任务", {'fields': (
                     "update_on_call_switch", "update_on_call_time",
                     "send_on_call_info_switch", "send_on_call_info_time",
                     ("send_on_call_info_reminder_type", "send_on_call_info_reminder_webhook"),
                     "clean_alert_inhibition_expired_switch",
                     ("clean_alert_inhibition_expired_period", "clean_alert_inhibition_expired_unit"),
                     "unresolved_alerts_reminder_switch", "alert_source",
                     ("unresolved_alerts_reminder_period", "unresolved_alerts_reminder_unit"),
                     ("unresolved_alerts_reminder_type","unresolved_alerts_reminder_webhook"),
                 )})),
                 )
    readonly_fields = ("configure_name",)
    form = SystemConfigureForm

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
