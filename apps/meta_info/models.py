from django.db import models


class MonitoringSystem(models.Model):
    """支持对接的监控系统"""
    name = models.CharField(max_length=50, unique=True, verbose_name='名称')
    desc = models.CharField(max_length=200, blank=True, verbose_name='描述')
    key = models.CharField(max_length=50, blank=True, verbose_name='Key')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '监控系统'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 生成附加属性，默认值"告警恢复时是否发送信息"
def gen_additional_attrs():
    return {"notify_when_alert_recovery": True}


class AlertMode(models.Model):
    """告警方式，如钉钉、微信等，每一类告警方式对应一个操作的类"""
    mode_name = models.CharField(max_length=20, unique=True, verbose_name='名称')
    module_path = models.CharField(max_length=100, verbose_name='类路径')
    module_name = models.CharField(max_length=100, verbose_name='类名称')
    additional_attrs = models.JSONField(default=gen_additional_attrs, verbose_name='附加属性')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '告警方式'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.mode_name
