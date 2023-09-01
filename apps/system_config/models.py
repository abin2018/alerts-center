from django.db import models
from apps.alerting.models import AlertSource
from datetime import time


class SystemConfigure(models.Model):
    unit_choices = (('minutes', '分钟'), ('hours', '小时'))

    configure_name = models.CharField(max_length=40, default='默认配置', verbose_name='配置名称')
    update_on_call_switch = models.BooleanField(default=False, verbose_name='更新值班表')
    update_on_call_time = models.TimeField(default=time(17, 0, 0), verbose_name='更新时间')
    send_on_call_info_switch = models.BooleanField(default=False, verbose_name='推送值班信息')
    send_on_call_info_time = models.TimeField(default=time(8, 40, 0), verbose_name='推送时间')
    send_on_call_info_reminder_type = models.CharField(max_length=20, default='dingding',
                                                       choices=(('dingding', '钉钉'), ('feishu', '飞书')),
                                                       verbose_name='通知方式')
    send_on_call_info_reminder_webhook = models.CharField(max_length=200, default='请设置', verbose_name='通知Webhook')
    clean_alert_inhibition_expired_switch = models.BooleanField(default=True, verbose_name='清理过期的告警抑制规则')
    clean_alert_inhibition_expired_period = models.SmallIntegerField(default=5, verbose_name='更新周期')
    clean_alert_inhibition_expired_unit = models.CharField(max_length=20, default='minutes',
                                                           choices=unit_choices, verbose_name='单位')
    unresolved_alerts_reminder_switch = models.BooleanField(default=False, verbose_name='未恢复告警提醒')
    alert_source = models.ManyToManyField(AlertSource, blank=True, verbose_name='需要提醒的告警源')
    unresolved_alerts_reminder_period = models.SmallIntegerField(default=1, verbose_name='提醒周期')
    unresolved_alerts_reminder_unit = models.CharField(max_length=20, default='hours',
                                                       choices=unit_choices, verbose_name='单位')
    unresolved_alerts_reminder_type = models.CharField(max_length=20, default='dingding',
                                                       choices=(('dingding', '钉钉'), ('feishu', '飞书')),
                                                       verbose_name='通知方式')
    unresolved_alerts_reminder_webhook = models.CharField(max_length=200, default='请设置', verbose_name='通知Webhook')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.configure_name


