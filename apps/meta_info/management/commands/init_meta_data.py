from apps.meta_info.models import MonitoringSystem
from apps.meta_info.models import AlertMode
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    init_data_monitoring_system = (
        ('Zabbix', 'Zabbix', 'zabbix'),
        ('阿里云监控', '阿里云监控', 'aliyun'),
        ('听云监控', '听云监控', 'tingyun'),
    )
    init_data_alert_mode = (
        ('钉钉', 'apps.messages.dingding', 'DingdingMessageSending'),
        ('飞书', 'apps.messages.feishu', 'FeishuMessageSending'),
        ('电话', 'apps.messages.voice', 'VoiceMessageSending'),
        ('邮箱', 'apps.messages.emails', 'EmailMessageSending'),
    )

    def handle(self, *args, **options):
        for _ in self.init_data_monitoring_system:
            name, desc, key = _
            MonitoringSystem.objects.get_or_create(name=name, desc=desc, key=key)
        for _ in self.init_data_alert_mode:
            mode_name, module_path, module_name = _
            AlertMode.objects.get_or_create(mode_name=mode_name, module_path=module_path, module_name=module_name)
        # 特殊属性设置，当告警恢复时，默认不打语音电话
        voice = AlertMode.objects.get(mode_name='电话')
        voice.additional_attrs['notify_when_alert_recovery'] = False
        voice.save()
