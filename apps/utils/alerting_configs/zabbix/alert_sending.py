import json
import sys
import os
import requests
import logging


# 日志设置
class ContextFilter(logging.Filter):
    """
    为日志记录添加PID作为logid的Filter
    """
    def filter(self, record):
        log_id = os.getpid()
        record.logid = log_id
        return True


log_file = '/tmp/alarm_send.log'
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
logid_filter = ContextFilter()
file_handler.addFilter(logid_filter)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(logid)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

try:
    # trigger_source = "{{ source_id }}"
    alarm_info_str, role = sys.argv[1:]
    alarm_info = json.loads(alarm_info_str)
    # alarm_info['alert_source'] = trigger_source
    # 处理级别
    alarm_info['alert_level'] = int(alarm_info['alert_level'])
    # 处理触发器状态
    if alarm_info['trigger_status'] == '0':
        alarm_info['alert_status'] = 'ok'
    elif alarm_info['trigger_status'] == '1':
        alarm_info['alert_status'] = 'firing'
    else:
        alarm_info['alert_status'] = 'unknown'
    # 处理主机组
    alarm_info['alert_object_groups'] = alarm_info['alert_object_groups'].split(', ')
    # 处理主机标签
    alert_object_label_dict = {}
    for label_str in alarm_info['alert_object_label'].split(", "):
        k, v = label_str.split(':')[:2]
        alert_object_label_dict[k] = v
    alarm_info['alert_object_label'] = alert_object_label_dict
    alarm_info['event_time'] = alarm_info['event_date'] + ' ' + alarm_info['event_clock']  # 需要处理为时间格式
    alarm_info['role'] = role
    # logger.info(alarm_info)
except Exception as e:
    logger.info(sys.argv)
    logger.exception(e)
    sys.exit()

url = '{{ request_scheme }}://{{ http_host }}/alerting/common/{{ source_id }}/'
try:
    requests.post(url, data=json.dumps(alarm_info), headers={'Content-Type': 'application/json'})
except Exception as e:
    logger.exception(e)

