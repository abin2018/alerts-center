from alerts_center.celery import app
from alerts_center.celery import CustomTask
from alerts_center.celery import celery_logger
from apps.on_call.models import OnCallStuff
from apps.on_call.models import OnCallTable
from apps.messages.dingding import DingdingMessageSending
from apps.messages.feishu import FeishuMessageSending
from django_celery_beat.models import PeriodicTask
import json


@app.task(name='更新值班表', shared=False, lazy=False, base=CustomTask)
def update_on_call_table():
    on_call_table, tag = OnCallTable.objects.get_or_create(sequence_name='on_call')
    sequence = on_call_table.sequence
    if sequence == {}:
        celery_logger.info('未找到值班表，执行初始化值班表')
        for role in set([obj.on_call_role.role_name for obj in OnCallStuff.objects.all()]):
            sequence[role] = 0
        on_call_table.save()
    else:
        sequence_tmp = sequence
        for role, number in sequence.items():
            if number + 1 == len(OnCallStuff.objects.filter(on_call_role__role_name=role)):
                sequence_tmp[role] = 0
            else:
                sequence_tmp[role] = sequence_tmp[role] + 1
        on_call_table.sequence = sequence_tmp
        on_call_table.save()
    # 更新完成值班表后发送一次信息
    task_send_on_call_info = PeriodicTask.objects.get(task='推送值班信息')
    send_on_call_info.delay(*json.loads(task_send_on_call_info.args), **json.loads(task_send_on_call_info.kwargs))


def get_on_call_stuff(role):
    """
    获取值班人员信息
    :param role:
    :return:
    """
    on_call_table, tag = OnCallTable.objects.get_or_create(sequence_name='on_call')
    sequence = on_call_table.sequence
    sequence_number = sequence[role]
    on_call_stuff = OnCallStuff.objects.filter(on_call_role__role_name=role).order_by('rank_number')[sequence_number]
    return on_call_stuff


@app.task(name='推送值班信息', shared=False, lazy=False, base=CustomTask)
def send_on_call_info(webhook, alert_mode='dingding', **kwargs):
    on_call_table, tag = OnCallTable.objects.get_or_create(sequence_name='on_call')
    reminder_text = "今日值班人员:\n"
    if alert_mode == 'dingding':
        at_list = []
        for role, seq in on_call_table.sequence.items():
            on_call_stuff = get_on_call_stuff(role)
            stuff_phone_number = on_call_stuff.stuff_phone_number
            at_list.append(stuff_phone_number)
            reminder_text += "{}: @{}\n".format(role, stuff_phone_number)
        reminder_text = reminder_text.strip()
        msg_body = {
            "msgtype": "text",
            "text": {
                "content": reminder_text
            },
        }
        msg_body['at'] = {}
        msg_body['at']["atMobiles"] = at_list
        msg_body['at']["isAtAll"] = False
        dingding = DingdingMessageSending(message_body=msg_body, target=webhook)
        return dingding.send()
    else:
        for role, seq in on_call_table.sequence.items():
            on_call_stuff = get_on_call_stuff(role)
            reminder_text += "{}: {}\n".format(role, on_call_stuff.stuff_name)
        msg_body = {
            "msg_type": "text",
            "content": {
                "text": reminder_text
            },
        }
        feishu = FeishuMessageSending(message_body=msg_body, target=webhook, is_at_all=True)
        feishu.add_at_info()
        print(feishu.message_body)
        return feishu.send_text_msg(reminder_text)