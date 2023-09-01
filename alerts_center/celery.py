from celery import Celery
from celery import Task
from django.conf import settings
from apps.messages.dingding import DingdingMessageSending
from celery.utils.log import get_task_logger
import os

# 设置django settings模块，参考manage.py
profile = os.environ.get('DJANGO_PROFILE')  # 需配置环境变量，设置使用local还是production的配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alerts_center.settings.{}'.format(profile))

# 初始化app
app = Celery('alerts_center')
celery_logger = get_task_logger(__name__)


# 指定CELERY配置，所有以CELERY开头的变量为celery的配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 所有django注册的app自动加载celery配置
app.autodiscover_tasks()


# 一个自定义的Task,设置了失败的处理机制
CELERY_MONITOR_DINGDING_WEBHOOK_URL = os.environ.get('CELERY_MONITOR_DINGDING_API_URL')
CELERY_MONITOR_DINGDING_WEBHOOK_SEC = os.environ.get('CELERY_MONITOR_DINGDING_API_SEC')


class CustomTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, error_info):
        exception_message = '任务"{}"执行失败,任务id:{}'.format(self.name, task_id)
        dingding = DingdingMessageSending(message_body={}, target=CELERY_MONITOR_DINGDING_WEBHOOK_URL,
                                          secret=CELERY_MONITOR_DINGDING_WEBHOOK_SEC)
        dingding.send_text_msg(exception_message)
        return super(CustomTask, self).on_failure(exc, task_id, args, kwargs, error_info)