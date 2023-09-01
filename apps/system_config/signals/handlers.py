from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.system_config.models import SystemConfigure
import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
import pytz


@receiver(post_save, sender=SystemConfigure, dispatch_uid="update_period_task")
def update_period_task(sender, instance, **kwargs):
    try:
        on_call_task = PeriodicTask.objects.get(task='更新值班表')
    except PeriodicTask.DoesNotExist:
        on_call_task = PeriodicTask(task='更新值班表')
    on_call_task.name = '更新值班表'
    on_call_task.enabled = instance.update_on_call_switch
    on_call_task_schedule, _ = CrontabSchedule.objects.get_or_create(minute='{}'.format(
        instance.update_on_call_time.minute),
                                                                     hour='{}'.format(
                                                                         instance.update_on_call_time.hour),
                                                                     day_of_week='*',
                                                                     day_of_month='*',
                                                                     timezone=pytz.timezone('Asia/Shanghai'))
    on_call_task.crontab = on_call_task_schedule
    on_call_task.save()


    try:
        send_on_call_info = PeriodicTask.objects.get(task='推送值班信息')
    except PeriodicTask.DoesNotExist:
        send_on_call_info = PeriodicTask(task='推送值班信息')
    send_on_call_info.name = '推送值班信息'
    send_on_call_info.enabled = instance.send_on_call_info_switch
    send_on_call_info_schedule, _ = CrontabSchedule.objects.get_or_create(minute='{}'.format(
        instance.send_on_call_info_time.minute),
                                                                     hour='{}'.format(
                                                                         instance.send_on_call_info_time.hour),
                                                                     day_of_week='*',
                                                                     day_of_month='*',
                                                                     timezone=pytz.timezone('Asia/Shanghai'))
    send_on_call_info.crontab = send_on_call_info_schedule
    args = [instance.send_on_call_info_reminder_webhook]
    send_on_call_info.args = json.dumps(args)
    kwargs = {"alert_mode": instance.send_on_call_info_reminder_type}
    send_on_call_info.kwargs = json.dumps(kwargs)
    send_on_call_info.save()



    try:
        clean_alert_inhibition_expired_task = PeriodicTask.objects.get(task='清理过期的告警抑制规则')
    except PeriodicTask.DoesNotExist:
        clean_alert_inhibition_expired_task = PeriodicTask(task='清理过期的告警抑制规则')
    clean_alert_inhibition_expired_task.name = '清理过期的告警抑制规则'
    clean_alert_inhibition_expired_task.enabled = instance.clean_alert_inhibition_expired_switch
    clean_alert_inhibition_expired_task_schedule, _ = IntervalSchedule.objects.get_or_create(
        every=instance.clean_alert_inhibition_expired_period,
        period=instance.clean_alert_inhibition_expired_unit
    )
    clean_alert_inhibition_expired_task.interval = clean_alert_inhibition_expired_task_schedule
    clean_alert_inhibition_expired_task.save()

    try:
        unresolved_alerts_reminder_period_task = PeriodicTask.objects.get(task='未恢复告警提醒')
    except PeriodicTask.DoesNotExist:
        unresolved_alerts_reminder_period_task = PeriodicTask(task='未恢复告警提醒')
    unresolved_alerts_reminder_period_task.name = '未恢复告警提醒'
    unresolved_alerts_reminder_period_task.enabled = instance.unresolved_alerts_reminder_switch
    unresolved_alerts_reminder_period_task_schedule, _ = IntervalSchedule.objects.get_or_create(
        every=instance.unresolved_alerts_reminder_period,
        period=instance.unresolved_alerts_reminder_unit
    )
    unresolved_alerts_reminder_period_task.interval = unresolved_alerts_reminder_period_task_schedule
    alert_source_ids = [_.source_id for _ in instance.alert_source.all()]
    args = [instance.unresolved_alerts_reminder_webhook] + alert_source_ids
    unresolved_alerts_reminder_period_task.args = json.dumps(args)
    kwargs = {"alert_mode": instance.unresolved_alerts_reminder_type}
    unresolved_alerts_reminder_period_task.kwargs = json.dumps(kwargs)
    unresolved_alerts_reminder_period_task.save()
