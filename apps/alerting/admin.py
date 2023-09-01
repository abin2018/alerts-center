import os.path
from django.contrib import admin
from django.http import JsonResponse
from django.http import FileResponse
from django.utils.safestring import mark_safe
from django.contrib import messages
from .models import AlertSource
from .models import AlertContent
from .models import AlertTemplate
from .models import AlertTarget
from .models import AlertRules
from .models import AlertInhibition
from .forms import AlertRulesForm
from .forms import AlertTargetForm
from .forms import AlertTemplateForm
from .forms import AlertInhibitionForm
from simpleui.admin import AjaxAdmin
from django.forms import widgets
from django.db.models import JSONField
from jinja2 import Environment, FileSystemLoader
from zipfile import ZipFile
import json


class PrettyJSONWidget(widgets.Textarea):
    """
    展示Json表单的Widget
    """
    def format_value(self, value):
        try:
            value = json.dumps(json.loads(value), indent=2, sort_keys=True, ensure_ascii=False)
            row_lengths = [len(r) for r in value.split('\n')]
            self.attrs['rows'] = 5
            self.attrs['cols'] = 97
            # self.attrs['rows'] = min(max(len(row_lengths) + 2, 10), 30)
            # self.attrs['cols'] = min(max(max(row_lengths) + 2, 40), 100)
            return value
        except Exception as e:
            return super(PrettyJSONWidget, self).format_value(value)


class JsonAdmin(AjaxAdmin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }


@admin.register(AlertSource)
class AlertSourceAdmin(JsonAdmin):
    list_display = ("name", "monitoring_system", "desc", "source_id", "create_time", "update_time")
    list_filter = ("monitoring_system", )
    search_fields = ("name", "source_id")
    readonly_fields = ('source_id',)
    actions = ["export_alert_configs"]

    def get_real_ip(self, request):
        http_server_addr = request.META.get('HTTP_SERVER_ADDR')
        http_server_port = request.META.get('HTTP_SERVER_PORT')
        if http_server_addr and http_server_port:
            if http_server_port == 80:
                return http_server_addr
            return "{}:{}".format(http_server_addr, http_server_port)
        return request.META.get("HTTP_HOST")

    def gen_zabbix_configs(self, request, alert_source_object):
        base_path = './apps/utils/alerting_configs/zabbix'
        configs_file_path = os.path.join(base_path, 'zabbix_configs.zip')
        env = Environment(loader=FileSystemLoader(base_path))
        script_template = env.get_template('alert_sending.py')
        script = script_template.render(
            source_id=alert_source_object.source_id,
            request_scheme=request.scheme,
            http_host=self.get_real_ip(request))
        zabbix_configs = ZipFile(configs_file_path, 'w')
        zabbix_configs.writestr('zabbix_alert_sending.py', script)
        with open(os.path.join(base_path, 'zbx_export_mediatypes_example.yaml'), encoding='utf8') as f:
            zabbix_configs.writestr('zbx_export_mediatypes_example.yaml', f.read())
        with open(os.path.join(base_path, 'zbx_export_mediatypes_v5.xml'), encoding='utf8') as f:
            zabbix_configs.writestr('zbx_export_mediatypes_v5.xml', f.read())
        with open(os.path.join(base_path, 'zbx_export_mediatypes_v6_0.yaml'), encoding='utf8') as f:
            zabbix_configs.writestr('zbx_export_mediatypes_v6_0.yaml', f.read())
        with open(os.path.join(base_path, 'zbx_export_mediatypes_v6_4.yaml'), encoding='utf8') as f:
            zabbix_configs.writestr('zbx_export_mediatypes_v6_4.yaml', f.read())
        with open(os.path.join(base_path, '配置文档.docx'), 'rb') as f:
            zabbix_configs.writestr('配置文档.docx', f.read())
        return configs_file_path

    def gen_aliyun_configs(self, request, alert_source_object):
        base_path = './apps/utils/alerting_configs/aliyun'
        configs_file_path = os.path.join(base_path, 'aliyun_configs.zip')
        env = Environment(loader=FileSystemLoader(base_path))
        readme_file_template = env.get_template('readme_aliyun.md')
        readme_file = readme_file_template.render(
            source_id=alert_source_object.source_id,
            request_scheme=request.scheme,
            http_host=self.get_real_ip(request))
        aliyun_configs = ZipFile(configs_file_path, 'w')
        aliyun_configs.writestr('readme_aliyun.md', readme_file)
        return configs_file_path

    def gen_tingyun_configs(self, request, alert_source_object):
        base_path = './apps/utils/alerting_configs/tingyun'
        configs_file_path = os.path.join(base_path, 'tingyun_configs.zip')
        env = Environment(loader=FileSystemLoader(base_path))
        readme_file_template = env.get_template('readme_tingyun.md')
        readme_file = readme_file_template.render(
            source_id=alert_source_object.source_id,
            request_scheme=request.scheme,
            http_host=self.get_real_ip(request))
        tingyun_configs = ZipFile(configs_file_path, 'w')
        tingyun_configs.writestr('readme_aliyun.md', readme_file)
        return configs_file_path

    def export_alert_configs(self, request, queryset):
        alert_source_object = queryset[0]
        key = alert_source_object.monitoring_system.key
        configs_file_path = getattr(self, "gen_{}_configs".format(key))(request, alert_source_object)
        file_name = os.path.split(configs_file_path)[-1]
        response = FileResponse(open(configs_file_path, "rb"))
        response['content-type'] = "application/octet-stream"
        # 如果直接传入file_name，file_name为中文无法正常解析
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)
        return response

    export_alert_configs.short_description = ' 下载告警配置文档'
    export_alert_configs.type = 'success'
    export_alert_configs.icon = 'fas fa-download'
    export_alert_configs.style = 'background-color:#00BFFF;border:1px solid #00BFFF;'


@admin.register(AlertContent)
class AlertContentAdmin(JsonAdmin):
    list_display = ("alert_source", "alert_id", "alert_object", "alert_object_ip",
                    "alert_content", "alert_level", "show_alert_status",
                    "latest_value", "assigned_role", "assigned_stuff", "trigger_time", "recovery_time")
    readonly_fields = ("alert_source", "alert_id", "alert_object", "alert_object_ip", "alert_object_groups",
                       "alert_object_label", "alert_content", "alert_level", "monitor_template", "alert_status",
                       "latest_value", "assigned_role", "assigned_stuff", "trigger_time",
                       "recovery_time", "update_time", "manually_close")
    list_filter = ("alert_source", "alert_status", "assigned_role")
    actions = ("manually_close",)
    search_fields = ("alert_id", "alert_content", "alert_object")

    def show_alert_status(self, obj):
        alert_status = obj.alert_status
        if alert_status == 'ok':
            return mark_safe('<span style="color:green">正常</span>')
        else:
            return mark_safe('<span style="color:red">告警</span>')

    show_alert_status.short_description = "告警状态"

    def manually_close(self, request, queryset):
        post = request.POST
        if not post.get('_selected'):
            return JsonResponse(data={
                'status': 'error',
                'msg': '请先选中数据！'
            })
        acknowledge_info = post.get('acknowledge_info').strip()
        for alert_content_obj in queryset:
            if alert_content_obj.alert_status == 'ok':
                continue
            alert_content_obj.manually_close = True
            alert_content_obj.alert_status = 'ok'
            alert_content_obj.acknowledge_info = acknowledge_info
            alert_content_obj.save()
        return JsonResponse(data={
            'status': 'success',
            'msg': '执行成功'
        })

    manually_close.short_description = ' 手动关闭'
    manually_close.type = 'success'
    manually_close.icon = 'fas fa-check-circle'
    manually_close.layer = {
        'title': '批量确认',
        'tips': '填写确认信息',
        'confirm_button': '确定',
        'cancel_button': '取消',
        'width': '40%',
        'labelWidth': "160px",
        'params': [{
            'type': 'textarea',
            'key': 'acknowledge_info',
            'label': '确认信息',
            'require': True
        }]
    }

    def has_add_permission(self, request):
        return False


@admin.register(AlertTemplate)
class AlertTemplateAdmin(JsonAdmin):
    list_display = ('template_name', 'alert_mode', 'template_content', 'create_time', 'update_time')
    list_filter = ('alert_mode',)
    search_fields = ("template_name",)
    form = AlertTemplateForm


@admin.register(AlertTarget)
class AlertTargetAdmin(JsonAdmin):
    list_display = ("target_name", "alert_mode", "target_content", "create_time", "update_time")
    list_filter = ("alert_mode",)
    search_fields = ("target_name",)
    form = AlertTargetForm


@admin.register(AlertRules)
class AlertRulesAdmin(JsonAdmin):
    fieldsets = (('规则信息', {'fields': ("rule_name",)}),
                 (("规则内容", {'fields': (
                     "week_day",
                     ("start_time", "end_time"),
                     "alert_source",
                     ("alert_object", "alert_object_operator"),
                     ("alert_object_ip", "alert_object_ip_operator"),
                     ("alert_object_groups", "alert_object_groups_operator"),
                     ("alert_content", "alert_content_operator"),
                     ("alert_object_label", "alert_object_label_operator"),
                     "alert_level",
                     ('monitor_template', 'monitor_template_operator'),
                     "assigned_roles",
                 )})),
                 (("告警信息",
                   {'fields': (
                       "alert_mode", "alert_template", "alert_target", "additional_args", "is_on_call", "is_working"
                   )}))
                 )
    list_display = ("rule_name", "alert_mode", "show_week_day", "show_alert_time", "show_alert_source",
                    "show_alert_object_ip", "show_alert_content", "show_assigned_roles", "alert_target",
                    "is_on_call", "is_working", "create_time", "update_time")
    search_fields = ("rule_name",)
    list_filter = ("alert_source", "alert_mode")
    actions = ("close_rules", "open_rules")
    form = AlertRulesForm

    def show_week_day(self, obj):
        return obj.get_week_day_display()
    show_week_day.short_description = "周"

    def show_alert_time(self, obj):
        return "{}-{}".format(obj.start_time, obj.end_time)
    show_alert_time.short_description = "告警时间"

    def show_alert_source(self, obj):
        return ",".join([_.name for _ in obj.alert_source.all()])
    show_alert_source.short_description = "告警源"

    def show_alert_object_ip(self, obj):
        return "({}){}".format(obj.get_alert_object_ip_operator_display(), obj.alert_object_ip)
    show_alert_object_ip.short_description = "告警对象IP"

    def show_alert_content(self, obj):
        if obj.alert_content:
            return "({}){}".format(obj.get_alert_content_operator_display(), obj.alert_content)
        return ""
    show_alert_content.short_description = "告警内容"

    def show_assigned_roles(self, obj):
        return ",".join([_.role_name for _ in obj.assigned_roles.all()])
    show_assigned_roles.short_description = "分配角色"

    def close_rules(self, request, queryset):
        for alert_rules_obj in queryset:
            alert_rules_obj.is_working = False
            alert_rules_obj.save()
            messages.add_message(request, messages.INFO, '{} 规则已关闭'.format(alert_rules_obj.rule_name))

    close_rules.short_description = " 关闭规则"
    close_rules.type = 'danger'
    close_rules.icon = 'fas fa-times-circle'

    def open_rules(self, request, queryset):
        for alert_rules_obj in queryset:
            alert_rules_obj.is_working = True
            alert_rules_obj.save()
            messages.add_message(request, messages.INFO, '{} 规则已启用'.format(alert_rules_obj.rule_name))

    open_rules.short_description = " 启用规则"
    open_rules.type = 'success'
    open_rules.icon = 'fas fa-check-circle'


@admin.register(AlertInhibition)
class AlertInhibitionAdmin(JsonAdmin):
    list_display = ("title", "inhibition_start_datetime", "inhibition_end_datetime", "alert_object",
                    "alert_object_ip", "alert_content_keyword", "create_time", "update_time")
    list_filter = ("alert_source",)
    search_fields = ("title", "alert_content_keyword")
    form = AlertInhibitionForm
