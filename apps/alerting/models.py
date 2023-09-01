from django.db import models
from smart_selects.db_fields import ChainedForeignKey
from multiselectfield import MultiSelectField
from datetime import time
from hashlib import md5
import random
from apps.meta_info.models import MonitoringSystem
from apps.meta_info.models import AlertMode
from apps.on_call.models import OnCallRole
from apps.on_call.models import OnCallStuff

# 告警级别选项
alert_level_choices = ((0, '未分类'), (1, '信息'), (2, '警告'), (3, '一般严重'), (4, '严重'), (5, '灾难'))


class AlertSource(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='名称')
    monitoring_system = models.ForeignKey(MonitoringSystem, on_delete=models.CASCADE, related_name='alert_source',
                                          verbose_name='监控系统')
    desc = models.CharField(max_length=200, blank=True, verbose_name='描述')
    source_id = models.CharField(max_length=50, unique=True, verbose_name='源ID')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.pk is None:
            _md5 = md5()
            _md5.update(str(random.random()).encode('utf8'))
            source_id = _md5.hexdigest()
            self.source_id = source_id
        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = '告警源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class AlertContent(models.Model):
    alert_status_choices = (('firing', '警报'), ('ok', '正常'), ('unknown', '未知'))

    alert_source = models.ForeignKey(AlertSource, null=True, on_delete=models.SET_NULL,
                                     related_name='alert_content', verbose_name='告警源')
    alert_id = models.CharField(max_length=50, verbose_name='告警ID')
    alert_object = models.CharField(max_length=200, verbose_name='告警对象')
    alert_object_ip = models.GenericIPAddressField(default='0.0.0.0', verbose_name='告警对象IP')
    alert_object_groups = models.JSONField(default=list, verbose_name='告警对象属组')
    alert_object_label = models.JSONField(default=dict, verbose_name='告警对象标签')
    alert_content = models.CharField(max_length=200, verbose_name='告警内容')
    alert_level = models.SmallIntegerField(choices=alert_level_choices, verbose_name='告警级别')
    monitor_template = models.CharField(max_length=200, blank=True, verbose_name='监控模板')
    alert_status = models.CharField(max_length=20, choices=alert_status_choices, verbose_name='告警状态')
    latest_value = models.CharField(max_length=200, verbose_name='最新值')
    assigned_role = models.ForeignKey(OnCallRole, blank=True, null=True, on_delete=models.SET_NULL,
                                      related_name='alert_content', verbose_name='分配角色')
    assigned_stuff = models.ForeignKey(OnCallStuff, blank=True, null=True, on_delete=models.SET_NULL,
                                       related_name='alert_content', verbose_name='分配人员')
    trigger_time = models.DateTimeField(blank=True, null=True, verbose_name='告警触发时间')
    recovery_time = models.DateTimeField(blank=True, null=True, verbose_name='告警恢复时间')
    manually_close = models.BooleanField(default=False, verbose_name='手动关闭')
    acknowledge_info = models.TextField(max_length=200, blank=True, verbose_name='确认信息')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '告警内容'
        verbose_name_plural = verbose_name
        unique_together = ["alert_source", "alert_id"]

    def __str__(self):
        return self.alert_id


class AlertTemplate(models.Model):
    template_name = models.CharField(max_length=50, verbose_name='模板名称')
    alert_mode = models.ForeignKey(AlertMode, on_delete=models.CASCADE, related_name='alert_template',
                                   verbose_name='告警方式')
    template_content = models.JSONField(default=dict, verbose_name='模板内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '告警模板'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.template_name


class AlertTarget(models.Model):
    target_name = models.CharField(max_length=50, verbose_name='对象名称')
    alert_mode = models.ForeignKey(AlertMode, on_delete=models.CASCADE, related_name='alert_target',
                                   verbose_name='告警方式')
    target_content = models.CharField(max_length=200, verbose_name='对象地址')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '告警对象'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.target_name


class AlertRules(models.Model):
    weekday_choices = ((0, '周一'), (1, '周二'), (2, '周三'), (3, '周四'), (4, '周五'), (5, '周六'), (6, '周日'))
    contains_choices = ((1, '不包含'), (0, '包含'))
    match_choices = ((1, '不匹配'), (0, '匹配'))

    rule_name = models.CharField(max_length=50, verbose_name='规则名称')
    # Time Filter
    week_day = MultiSelectField(default=[0, 1, 2, 3, 4, 5, 6], max_length=30, choices=weekday_choices, verbose_name='周')
    start_time = models.TimeField(default=time(0, 0, 0), verbose_name='开始时间')
    end_time = models.TimeField(default=time(23, 59, 59), verbose_name='终止时间')
    # Alert Filter
    alert_source = models.ManyToManyField(AlertSource, verbose_name='告警源', related_name='alert_rules')
    alert_object = models.CharField(max_length=200, blank=True, verbose_name='告警对象')
    alert_object_operator = models.SmallIntegerField(default=0, choices=contains_choices, verbose_name='操作符')
    alert_object_ip = models.CharField(max_length=200, default='0.0.0.0', verbose_name='告警对象IP')
    alert_object_ip_operator = models.SmallIntegerField(default=0, choices=match_choices, verbose_name='操作符')
    alert_object_groups = models.CharField(max_length=200, blank=True, verbose_name='告警对象属组')
    alert_object_groups_operator = models.SmallIntegerField(default=0, choices=contains_choices, verbose_name='操作符')
    alert_content = models.CharField(max_length=200, blank=True, verbose_name='告警内容(关键字)')
    alert_content_operator = models.SmallIntegerField(default=0, choices=contains_choices, verbose_name='操作符')
    alert_object_label = models.JSONField(default=dict, blank=True, verbose_name='告警对象标签')
    alert_object_label_operator = models.SmallIntegerField(default=0, choices=contains_choices, verbose_name='操作符')
    # alert_level = models.SmallIntegerField(choices=alert_level_choices, verbose_name='告警级别')
    alert_level = MultiSelectField(default=[3, 4, 5], max_length=50, choices=alert_level_choices,
                                   verbose_name='告警级别')
    monitor_template = models.CharField(max_length=200, blank=True, verbose_name='监控模板')
    monitor_template_operator = models.SmallIntegerField(default=0, choices=contains_choices, verbose_name='操作符')
    # Assigned Role Filter
    assigned_roles = models.ManyToManyField(OnCallRole, verbose_name='分配角色', related_name='alert_rules')

    # Message
    alert_mode = models.ForeignKey(AlertMode, on_delete=models.CASCADE, related_name='alert_rules',
                                   verbose_name='告警方式')
    alert_template = ChainedForeignKey(AlertTemplate, chained_field='alert_mode', chained_model_field='alert_mode',
                                       show_all=False, auto_choose=True, verbose_name='告警模板')
    alert_target = ChainedForeignKey(AlertTarget, chained_field='alert_mode', chained_model_field='alert_mode',
                                     show_all=False, auto_choose=True, verbose_name='告警对象')
    additional_args = models.JSONField(default=dict, blank=True, verbose_name='告警方式附属参数')
    # OnCall
    is_on_call = models.BooleanField(default=False, verbose_name='是否同步值班信息')
    # switch
    is_working = models.BooleanField(default=True, verbose_name='是否开启')

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '告警规则'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.rule_name


def gen_alert_content_keyword():
    return ["端口"]


class AlertInhibition(models.Model):
    title = models.CharField(max_length=30, verbose_name='标题')
    inhibition_start_datetime = models.DateTimeField(verbose_name='抑制开始时间')
    inhibition_end_datetime = models.DateTimeField(verbose_name='抑制终止时间')
    alert_source = models.ManyToManyField(AlertSource, verbose_name='告警源', related_name='alert_inhibition')
    alert_object = models.JSONField(blank=True, default=list, verbose_name='告警对象')
    alert_object_ip = models.CharField(max_length=200, blank=True, verbose_name='维护对象IP',
                                       help_text="写法:192.168.1.1或192.168.1.1,"
                                                 "192.168.1.2或192.168.1.1-5或"
                                                 "192.168.1.0/32或192.168.1.1|3|5"
                                       )
    alert_content_keyword = models.JSONField(blank=True, default=gen_alert_content_keyword, verbose_name='告警内容(关键词)')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '告警抑制'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
