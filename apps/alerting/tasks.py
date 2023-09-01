from alerts_center.celery import app
from alerts_center.celery import CustomTask
from alerts_center.celery import celery_logger
from apps.on_call.models import OnCallRole
from apps.on_call.tasks import get_on_call_stuff
from apps.messages.dingding import DingdingMessageSending
from apps.messages.feishu import FeishuMessageSending
from .models import AlertSource
from .models import AlertContent
from .models import AlertRules
from .models import AlertInhibition
from .models import alert_level_choices
from apps.utils.utils import ip_string_parser
from apps.utils.utils import trans_camel_case
from datetime import datetime
from datetime import time
from importlib import import_module
import jinja2
import json
import re
import os


def apply_inhibition(alert_inhibition_object, alert_data):
    """
    应用每一个告警抑制规则
    :param alert_inhibition_object:
    :param alert_data:
    :return:
    """
    # 1.时间
    alert_now_datetime = datetime.now()
    inhibition_start_datetime = alert_inhibition_object.inhibition_start_datetime
    inhibition_end_datetime = alert_inhibition_object.inhibition_end_datetime
    alert_datetime_tag = inhibition_start_datetime <= alert_now_datetime <= inhibition_end_datetime
    # 2.告警源
    source_id = alert_data['alert_source']
    source_id_list = [obj.source_id for obj in alert_inhibition_object.alert_source.all()]
    alert_source_tag = source_id in source_id_list
    # 3.告警对象
    alert_object = alert_data['alert_object']
    inhibition_alert_objects = alert_inhibition_object.alert_object
    if not inhibition_alert_objects:
        alert_object_tag = True
    else:
        alert_object_tag = alert_object in inhibition_alert_objects
    # 4.告警对象IP
    alert_object_ip = alert_data['alert_object_ip']
    inhibition_alert_object_ip = alert_inhibition_object.alert_object_ip.strip()
    if not inhibition_alert_object_ip:
        alert_object_ip_tag = True
    else:
        try:
            alert_object_ip_tag = alert_object_ip in ip_string_parser(inhibition_alert_object_ip)
        except Exception as e:
            celery_logger.error(e)
            alert_object_ip_tag = False
    # 5.告警内容(关键词)
    alert_content = alert_data.get('alert_content')
    alert_content_keyword_tag = False
    alert_content_keywords = alert_inhibition_object.alert_content_keyword
    if not alert_content_keywords:
        alert_content_keyword_tag = True
    else:
        for keyword in alert_content_keywords:
            if keyword.lower() in alert_content.lower():
                alert_content_keyword_tag = True
                break
    return all([alert_datetime_tag, alert_source_tag, alert_object_tag, alert_object_ip_tag, alert_content_keyword_tag])


def process_alert_inhibition(alert_data):
    """
    应用所有告警抑制规则
    :param alert_data:
    :return:
    """
    alert_inhibition_objects = AlertInhibition.objects.all()
    for inhibition_object in alert_inhibition_objects:
        inhibition_tag = apply_inhibition(inhibition_object, alert_data)
        if inhibition_tag:
            return True, inhibition_object.title
    return False, None


@app.task(name='清理过期的告警抑制规则', shared=False, lazy=False, base=CustomTask)
def clean_alert_inhibition_expired():
    inhibition_objects = AlertInhibition.objects.all()
    for inhibition_object in inhibition_objects:
        if datetime.now() > inhibition_object.inhibition_end_datetime:
            inhibition_object.delete()


@app.task(name='处理收到的告警数据', shared=False, lazy=False, base=CustomTask, ignore_result=True)
def process_alerting_data(alert_data, save=True):
    # celery_logger.info(alert_data)
    # 检查是否抑制
    inhibition_tag, inhibition_title = process_alert_inhibition(alert_data)
    if inhibition_tag:
        celery_logger.info(alert_data)
        celery_logger.info('匹配到维护窗口:{}，退出'.format(inhibition_title))
        return
    alert_source = alert_data['alert_source']
    alert_source_object = AlertSource.objects.get(source_id=alert_source)
    alert_id = alert_data['alert_id']
    # 新增告警内容对象
    try:
        alert_content_object = AlertContent.objects.get(alert_source=alert_source_object, alert_id=alert_id)
    except AlertContent.DoesNotExist:
        alert_content_object = AlertContent()
        alert_content_object.alert_source = alert_source_object
        alert_content_object.alert_id = alert_id
    # 更新内容
    for field in ["alert_object", "alert_object_ip", "alert_object_groups", "alert_object_label", "alert_content",
                  "alert_level", "monitor_template", "alert_status", "latest_value"]:
        setattr(alert_content_object, field, alert_data[field])
    # 更新时间，可能为告警时间或者恢复时间，需加以区分
    event_time_string = alert_data['event_time']
    event_time = datetime.strptime(event_time_string, "%Y.%m.%d %H:%M:%S")
    if alert_data['alert_status'] == 'firing':
        alert_content_object.trigger_time = event_time
    elif alert_data['alert_status'] == 'ok':
        alert_content_object.recovery_time = event_time
    # 分配角色和值班人员
    role_name = alert_data['role']
    try:
        assigned_role_object, tag = OnCallRole.objects.get_or_create(role_name=role_name)
        if tag:
            celery_logger.info("创建新的角色:{}".format(role_name))
        assigned_stuff_object = get_on_call_stuff(role_name)
        alert_content_object.assigned_role = assigned_role_object
        alert_content_object.assigned_stuff = assigned_stuff_object
    except Exception as e:
        celery_logger.error(e)
    if save:
        alert_content_object.save()
    for alert_rule_obj in AlertRules.objects.all():
        process_alert_rules.delay(alert_rule_obj.pk, alert_data)


def process_aliyun_alert_data(alert_data_raw):
    # celery_logger.info(alert_data_raw)
    alert_data = dict()
    alert_data['alert_source'] = alert_data_raw['alert_source']
    alert_data['alert_id'] = alert_data_raw['transId'][0]
    metric_name = alert_data_raw.get('metricName', ['unknown_metric_name'])[0]
    expression = alert_data_raw.get('expression', ['unknown_expression'])[0]
    # 获取数字和符号部分
    expression_number_part = expression.strip('$Average').replace(' ', '')
    unit = alert_data_raw.get('unit', ['unknown_unit'])[0]
    if unit == '%':
        alert_content = '{}{}{}'.format(metric_name, expression_number_part, unit)
    else:
        alert_content = '{}{}'.format(metric_name, expression_number_part)
    last_time = alert_data_raw['lastTime'][0]
    alert_data['alert_content'] = "{}(持续时间{})".format(alert_content, last_time)
    trigger_level = alert_data_raw.get('triggerLevel')[0]
    pre_trigger_level = alert_data_raw.get('preTriggerLevel')[0]
    trigger_level_trans_dict = {'INFO': 1, 'WARN': 3, 'CRITICAL': 5}
    if trigger_level == 'OK':
        alert_level = trigger_level_trans_dict.get(pre_trigger_level, 5)
    else:
        alert_level = trigger_level_trans_dict.get(trigger_level, 5)
    alert_data['alert_level'] = alert_level
    alert_state = alert_data_raw.get('alertState')[0]
    alert_status = {'ALERT': 'firing', 'OK': 'ok', 'INSUFFICIENT_DATA': 'unknown'}.get(alert_state)
    alert_data['alert_status'] = alert_status
    instance_name = alert_data_raw['instanceName'][0]

    reg_ipaddr = re.compile(
        r'(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])'
        r'\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$')
    alert_object_ip_reg = reg_ipaddr.search(instance_name)
    if alert_object_ip_reg:
        alert_object_ip = alert_object_ip_reg.group()
    else:
        alert_object_ip = '0.0.0.0'
    alert_data['alert_object_ip'] = alert_object_ip

    reg_instance_name = re.search(r'端口：(.*)，实例名称：(.*)，实例ID：', instance_name)
    if reg_instance_name:
        try:
            port = reg_instance_name.groups()[0]
            instance_name_part = reg_instance_name.groups()[1]
            instance_name = "{}(端口:{})".format(instance_name_part, port)
        except Exception as e:
            celery_logger.error(e)
    alert_data['alert_object'] = instance_name

    alert_data['alert_object_groups'] = alert_data_raw['productGroupName']
    cur_value = alert_data_raw['curValue'][0]
    alert_data['latest_value'] = cur_value
    alert_data['alert_object_label'] = {
        'region_id': alert_data_raw['regionId'][0],
        'region_name': alert_data_raw['regionName'][0],
        'rule_id': alert_data_raw['ruleId'][0],
        'group_id': alert_data_raw['groupId'][0],
        'user_id': alert_data_raw['userId'][0],
        'alert_name': alert_data_raw['alertName'][0],
        'metric_project': alert_data_raw['metricProject'][0],
        'namespace': alert_data_raw['namespace'][0]
    }
    # 处理dimensions
    dimensions = alert_data_raw['dimensions'][0].replace('{', '').replace('}', '')

    dimensions_dict = {}
    try:
        for _ in dimensions.split(','):
            k, v = _.strip().split('=')
            dimensions_dict[trans_camel_case(k)] = v
    except Exception as e:
        celery_logger.error(e)
    alert_data['alert_object_label'].update(dimensions_dict)
    alert_data['monitor_template'] = alert_data_raw['rawMetricName'][0]
    timestamp = int(alert_data_raw.get('timestamp')[0]) / 1000
    trigger_time = datetime.fromtimestamp(timestamp)
    alert_data['event_time'] = trigger_time.strftime("%Y.%m.%d %H:%M:%S")
    # role
    namespace = alert_data['alert_object_label']['namespace']
    # 此处不要使用硬编码，后期需要更改
    namespace_role_dict = {
        "acs_ecs": "主机",
        "acs_rds": "数据库",
        "acs_slb": "网络"
    }
    if alert_data['alert_object_label']['user_id'] == os.environ.get("EGAOSU_USER_ID"):
        alert_data['role'] = 'e高速'
    else:
        alert_data['role'] = namespace_role_dict.get(namespace, '主机')
    return alert_data


def process_tingyun_alert_data(alert_data_raw):
    alert_data = dict()
    alert_data['alert_source'] = alert_data_raw['alert_source']
    alert_data['alert_id'] = alert_data_raw['trace_id']
    alert_data['alert_content'] = alert_data_raw['description']
    alert_level_dict = {'1': 3, '2': 5}
    alert_data['alert_level'] = alert_level_dict.get(alert_data_raw['event_level'], 5)
    system_name = alert_data_raw['system_name']
    app_name = alert_data_raw['app_name']
    alert_data['alert_object'] = '{}-{}'.format(system_name, app_name)
    reg_ipaddr = re.compile(
        r'(^\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])'
        r'\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$')
    reg_app_name = re.search(r'\d+_\d+_\d+_\d+', app_name)
    if reg_app_name:
        ip_get = reg_app_name.group().replace('_', '.')
        if reg_ipaddr.match(ip_get):
            alert_object_ip = ip_get
        else:
            alert_object_ip = '0.0.0.0'
    else:
        alert_object_ip = '0.0.0.0'
    alert_data['alert_object_ip'] = alert_object_ip
    alert_data['alert_object_groups'] = []
    alert_data['latest_value'] = alert_data_raw['value']
    alert_data['alert_object_label'] = {
        'system_name': alert_data_raw['system_name'],
        'app_name': alert_data_raw['app_name']
    }
    alert_data['monitor_template'] = alert_data_raw['metric']
    event_status = alert_data_raw['event_status']
    if event_status == '1':
        alert_data['alert_status'] = 'firing'
    else:
        alert_data['alert_status'] = 'ok'
    event_time = alert_data_raw['event_time']
    event_time_datetime = datetime.strptime(event_time, "%Y-%m-%d %H:%M:%S")
    alert_data['event_time'] = event_time_datetime.strftime("%Y.%m.%d %H:%M:%S")
    alert_data['role'] = '主机'
    return alert_data


@app.task(name='处理告警规则', shared=False, lazy=False, base=CustomTask, ignore_result=True)
def process_alert_rules(alert_rules_pk, alert_data):
    alert_rules_object = AlertRules.objects.get(pk=alert_rules_pk)

    # 1.先判断是否生效
    is_working = alert_rules_object.is_working
    if not is_working:
        celery_logger.info('规则{}未生效'.format(alert_rules_object.rule_name))
        return
    # 2.周
    today = datetime.today()
    week_day = [int(_) for _ in alert_rules_object.week_day]
    week_day_tag = today.weekday() in week_day
    # 3.时间
    alert_start_time = alert_rules_object.start_time
    alert_end_time = alert_rules_object.end_time
    # 当前时间的time格式
    now = datetime.now()
    alert_now_time = time(now.hour, now.minute, now.second)
    if alert_end_time > alert_start_time:
        now_time_tag = alert_start_time <= alert_now_time <= alert_end_time
    # 结束时间小于开始时间说明已经跨天
    else:
        now_time_tag = alert_start_time <= alert_now_time <= time(23, 59, 59) or \
                       time(0, 0) < alert_now_time < alert_end_time
    # 4.告警源
    alert_source = alert_data['alert_source']
    alert_rules_alert_source = [obj.source_id for obj in alert_rules_object.alert_source.all()]
    alert_source_tag = alert_source in alert_rules_alert_source

    # 获取触发器源名称
    alert_source_obj = AlertSource.objects.get(source_id=alert_source)
    alert_source_name = alert_source_obj.name
    alert_data["alert_source_name"] = alert_source_name

    # 5.告警对象
    alert_object = alert_data['alert_object']
    alert_rules_alert_object = alert_rules_object.alert_object
    alert_object_operator = alert_rules_object.alert_object_operator
    if not alert_rules_alert_object:
        alert_object_tag = True
    else:
        alert_object_tag = bool(
            (alert_object in [_.strip() for _ in alert_rules_alert_object.split(',')]) ^ alert_object_operator
        )

    # 6.告警对象IP
    alert_object_ip = alert_data['alert_object_ip']
    alert_rules_alert_object_ip = alert_rules_object.alert_object_ip
    alert_object_ip_operator = alert_rules_object.alert_object_ip_operator
    if alert_rules_alert_object_ip == '0.0.0.0':
        alert_object_ip_tag = True
    else:
        alert_object_ip_tag = bool(
            (alert_object_ip in ip_string_parser(alert_rules_alert_object_ip)) ^ alert_object_ip_operator
        )

    # 7.告警对象属组
    alert_object_groups = alert_data['alert_object_groups']
    alert_rules_alert_object_groups = alert_rules_object.alert_object_groups
    alert_object_groups_operator = alert_rules_object.alert_object_groups_operator
    if not alert_rules_alert_object_groups:
        alert_object_groups_tag = True
    else:
        alert_object_groups_tag = bool(
             bool(
                 set(alert_object_groups) & set([_.strip() for _ in alert_rules_alert_object_groups.split(',')])
             ) ^ alert_object_groups_operator
        )

    # 8.告警内容
    alert_content = alert_data['alert_content']
    alert_rules_alert_content = alert_rules_object.alert_content
    alert_content_operator = alert_rules_object.alert_content_operator
    if not alert_rules_alert_content:
        alert_content_tag = True
    else:
        alert_content_tag_tmp = False
        for keyword in [_.strip() for _ in alert_rules_alert_content.split(',')]:
            if keyword in alert_content:
                alert_content_tag_tmp = True
                continue
        alert_content_tag = bool(alert_content_tag_tmp ^ alert_content_operator)

    # 9.标签
    alert_object_label = alert_data['alert_object_label']
    alert_rules_alert_object_label = alert_rules_object.alert_object_label
    alert_object_label_operator = alert_rules_object.alert_object_label_operator
    if not alert_rules_alert_object_label:
        alert_object_label_tag = True
    else:
        alert_object_label_tag_tmp = False
        for k, v in alert_rules_alert_object_label.items():
            _v = alert_object_label.get(k)
            if v == _v:
                alert_object_label_tag_tmp = True
                continue
        alert_object_label_tag = bool(alert_object_label_tag_tmp ^ alert_object_label_operator)

    # 10.告警级别
    alert_level = alert_data['alert_level']
    alert_rules_alert_level = [int(_) for _ in alert_rules_object.alert_level]
    alert_level_tag = alert_level in alert_rules_alert_level
    # 修改alert_level的数字为文字级别
    alert_data['alert_level'] = dict(alert_level_choices).get(alert_level, '未知')

    # 11.监控模板
    monitor_template = alert_data['monitor_template']
    alert_rules_monitor_template = alert_rules_object.monitor_template
    monitor_template_operator = alert_rules_object.monitor_template_operator
    if not alert_rules_monitor_template:
        monitor_template_tag = True
    else:
        monitor_template_tag = bool(
            (monitor_template in [_.strip() for _ in alert_rules_monitor_template.split(',')]) ^
            monitor_template_operator
        )

    # 12.分配角色
    role = alert_data['role']
    alert_rules_role = alert_rules_object.assigned_roles
    role_tag = role in [obj.role_name for obj in alert_rules_role.all()]

    # 发送消息
    if all([week_day_tag, now_time_tag, alert_source_tag, alert_object_tag, alert_object_ip_tag,
            alert_object_groups_tag, alert_content_tag, alert_object_label_tag, alert_level_tag,
            monitor_template_tag, role_tag]):
        celery_logger.info("告警ID:{} 匹配告警规则:{}".format(alert_data["alert_id"], alert_rules_object.rule_name))
        # 获取告警模块
        alert_mode = alert_rules_object.alert_mode
        # 判断是否需要发送
        if alert_data['alert_status'] == 'ok' and not alert_mode.additional_attrs['notify_when_alert_recovery']:
            celery_logger.info("告警恢复时不通过{}方式发送".format(alert_mode.mode_name))
            return
        message_module = import_module(alert_mode.module_path)
        message_class = getattr(message_module, alert_mode.module_name)
        celery_logger.info("告警发送方式:{}".format(alert_mode.mode_name))
        # 获取并渲染告警模板
        alert_template_object = alert_rules_object.alert_template
        template_content = alert_template_object.template_content
        message_body_template = jinja2.Template(template_content)
        message_body_rendered = message_body_template.render(**alert_data)
        message_body = json.loads(message_body_rendered)
        # 获取告警对象
        alert_target_object = alert_rules_object.alert_target
        target_content = alert_target_object.target_content
        # celery_logger.info("发送目标:{}".format(target_content))
        message_sender = message_class(message_body=message_body, target=target_content)
        # 值班信息
        if alert_rules_object.is_on_call:
            try:
                on_call_stuff = get_on_call_stuff(role)
                message_sender.process_on_call(on_call_stuff)
                celery_logger.info('同步值班信息，值班人员:{}，角色:{}'.format(on_call_stuff, role))
                celery_logger.info("发送目标:{}".format(message_sender.target))
            except Exception as e:
                celery_logger.error('同步值班信息异常:{}'.format(e))
        # 附加信息
        if alert_rules_object.additional_args:
            celery_logger.info("处理附加信息:{}".format(alert_rules_object.additional_args))
            message_sender.process_additional_args(alert_rules_object.additional_args)
        celery_logger.info("发送返回值{}".format(message_sender.send()))
    else:
        celery_logger.info("告警ID:{} 不匹配告警规则:{}".format(alert_data["alert_id"], alert_rules_object.rule_name))
        celery_logger.info(
            """
            week_day_tag:{}
            now_time_tag:{}
            alert_source_tag:{}
            alert_object_tag:{}
            alert_object_ip_tag:{}
            alert_object_groups_tag:{}
            alert_content_tag:{}
            alert_object_label_tag:{}
            alert_level_tag:{}
            monitor_template_tag:{}
            role_tag:{}
            """.format(week_day_tag, now_time_tag, alert_source_tag, alert_object_tag, alert_object_ip_tag,
                       alert_object_groups_tag, alert_content_tag, alert_object_label_tag, alert_level_tag,
                       monitor_template_tag, role_tag)
        )


@app.task(name='未恢复告警提醒', shared=False, lazy=False, base=CustomTask)
def unresolved_alerts_reminder(webhook, *alert_source_ids, alert_mode='dingding', **kwargs):
    """
    支持钉钉和飞书的未恢复的告警的提醒
    :param webhook:
    :param alert_source_ids:
    :param alert_mode:
    :param kwargs:
    :return:
    """
    if alert_source_ids:
        unresolved_alerts = AlertContent.objects.filter(alert_source__source_id__in=alert_source_ids,
                                                        alert_status='firing')
    else:
        unresolved_alerts = AlertContent.objects.filter(alert_status='firing')

    at_list = []
    if alert_mode == 'dingding':
        reminder_text = '**<font color=#B22222>以下告警尚未恢复，请及时处理</font>**:\n'
    else:
        reminder_text = ''
    if unresolved_alerts:
        n = 1
        for alert_content_obj in unresolved_alerts:
            assigned_stuff = alert_content_obj.assigned_stuff
            if assigned_stuff:
                at_phone = assigned_stuff.stuff_phone_number
                at_list.append(at_phone)
            else:
                at_phone = ''
            if alert_mode == 'dingding':
                reminder_text += '{}. {}:{} {}(故障ID:{}) @{}\n'.format(n,
                                                                      alert_content_obj.alert_source.name,
                                                                      alert_content_obj.alert_object_ip,
                                                                      alert_content_obj.alert_content,
                                                                      alert_content_obj.alert_id,
                                                                      at_phone)
            else:
                reminder_text += '{}. {}:{} {}(故障ID:{})\n'.format(n,
                                                                  alert_content_obj.alert_source.name,
                                                                  alert_content_obj.alert_object_ip,
                                                                  alert_content_obj.alert_content,
                                                                  alert_content_obj.alert_id)
            n += 1

        if alert_mode == 'dingding':
            msg_body = {
                "msgtype": "markdown",
                "markdown": {
                    "title": '未恢复告警提醒',
                    "text": reminder_text
                },
                "at": {
                    "atMobiles": at_list,
                    "isAtAll": False
                }
            }
            dingding = DingdingMessageSending(message_body=msg_body, target=webhook)
            return dingding.send()
        else:
            msg_body = {
                "msg_type": "interactive",
                "card": {
                    "elements": [{
                        "tag": "div",
                        "text": {
                            "content": reminder_text,
                            "tag": "lark_md"
                        }
                    }
                   ],
                    "header": {
                        "title": {
                            "content": "<font color=red>以下告警尚未恢复，请及时处理</font>",
                            "tag": "lark_md"
                        }
                    }
                }
            }
            feishu = FeishuMessageSending(message_body=msg_body, target=webhook, is_at_all=True)
            feishu.add_at_info()
            return feishu.send()
