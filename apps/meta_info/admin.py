from django.contrib import admin
from .models import MonitoringSystem
from .models import AlertMode
from django_celery_beat.admin import PeriodicTaskAdmin

# simpleui的标题设置
admin.site.site_header = '告警管理'  # 设置header
admin.site.site_title = '告警管理'  # 设置title
admin.site.index_title = '告警管理'


@admin.register(MonitoringSystem)
class MonitoringSystemAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AlertMode)
class AlertModeAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# PeriodicTaskAdmin权限配置
def periodic_task_get_actions(self, request):
    ret_actions = {}
    actions = super(PeriodicTaskAdmin, self).get_actions(request)
    ret_actions['run_tasks'] = actions['run_tasks']
    return ret_actions


def periodic_task_has_add_permission(self, request, obj=None):
    return False


def periodic_task_has_delete_permission(self, request, obj=None):
    return False


def periodic_task_has_change_permission(self, request, obj=None):
    return False


PeriodicTaskAdmin.get_actions = periodic_task_get_actions
PeriodicTaskAdmin.has_add_permission = periodic_task_has_add_permission
PeriodicTaskAdmin.has_delete_permission = periodic_task_has_delete_permission
PeriodicTaskAdmin.has_change_permission = periodic_task_has_change_permission
PeriodicTaskAdmin.search_fields = []
PeriodicTaskAdmin.list_filter = []
