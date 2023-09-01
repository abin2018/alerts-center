from apps.alerting.models import AlertMode
from apps.alerting.models import AlertTemplate
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    alert_template_init = (
        ('钉钉默认模板',  '钉钉', '{\r\n  "markdown": {\r\n    {% if alert_status == \'firing\' %}\r\n        '
                    '"text": "**<font color=#B22222>告警发生</font>**\\n- 故障来源:{{ alert_source_name }}\\n- '
                    '故障类型:{{ role }}\\n- 故障IP:{{ alert_object_ip }}\\n- 故障对象:{{ alert_object }}\\n- '
                    '故障内容:{{ alert_content }}\\n- 故障时间:{{ event_time  }}\\n- 监控值:{{ latest_value  }}\\n- '
                    '故障ID:{{ alert_id }}",\r\n        "title": "告警发生"\r\n    {% else %}\r\n        '
                    '"text": "**<font color=#228B22>告警恢复</font>**\\n- 故障来源:{{ alert_source_name }}\\n- '
                    '故障类型:{{ role }}\\n- 故障IP:{{ alert_object_ip }}\\n- 故障对象:{{ alert_object }}\\n- '
                    '故障内容:{{ alert_content }}\\n- 恢复时间:{{ event_time  }}\\n- 监控值:{{ latest_value  }}\\n- '
                    '故障ID:{{ alert_id }}",\r\n        "title": "告警恢复"\r\n    {% endif %}\r\n  },\r\n  '
                    '"msgtype": "markdown"\r\n}'),
        ('邮箱默认模板', '邮箱', '{\r\n    {% if alert_status == \'firing\' %}\r\n        '
                   '"message": "故障来源:{{ alert_source_name }}\\n故障类型:{{ role }}\\n故障IP:{{ alert_object_ip }}\\n'
                   '故障对象:{{ alert_object }}\\n故障内容:{{ alert_content }}\\n故障时间:{{ event_time }}\\n '
                   '监控值:{{ latest_value }}\\n故障ID:{{ alert_id }}",\r\n        "subject": "告警发生"\r\n    '
                   '{% else %}\r\n        "message": "故障来源:{{ alert_source_name }}\\n故障类型:{{ role }}\\n'
                   '故障IP:{{ alert_object_ip }}\\n故障对象:{{ alert_object }}\\n 故障内容:{{ alert_content }}\\n'
                   '恢复时间:{{ event_time }}\\n 监控值:{{ latest_value  }}\\n故障ID:{{ alert_id }}",\r\n        '
                   '"subject": "告警恢复"\r\n    {% endif %}\r\n}'),
        ('飞书默认模板', '飞书', '{\r\n    "msg_type": "interactive",\r\n    "card": {\r\n        "elements": [{\r\n'
                         '            "tag": "div",\r\n            "text": {\r\n                 '
                         '{% if alert_status == \'firing\' %}\r\n                    '
                         '"content": "---> 故障来源:{{ alert_source_name }}\\n---> 故障类型:{{ role }}\\n---> '
                         '故障IP:{{ alert_object_ip }}\\n---> 故障对象:{{ alert_object }}\\n---> '
                         '故障内容:{{ alert_content }}\\n---> 故障时间:{{ event_time }}\\n---> '
                         '监控值:{{ latest_value }}\\n---> 故障ID:{{ alert_id }}",\r\n                 '
                         '{% else %}\r\n                    "content": "---> 故障来源:{{ alert_source_name }}'
                         '\\n---> 故障类型:{{ role }}\\n---> 故障IP:{{ alert_object_ip }}\\n---> '
                         '故障对象:{{ alert_object }}\\n---> 故障内容:{{ alert_content }}\\n---> '
                         '恢复时间:{{ event_time }}\\n---> 监控值:{{ latest_value }}\\n---> '
                         '故障ID:{{ alert_id }}",\r\n                 {% endif %}\r\n                '
                         '"tag": "lark_md"\r\n            }\r\n        }\r\n       ],\r\n        '
                         '"header": {\r\n            "title": {\r\n                '
                         '{% if alert_status == \'firing\' %}\r\n                    '
                         '"content": "<font color=red>告警发生</font>",\r\n                '
                         '{% else %}\r\n "content": "<font color=green>告警恢复</font>",\r\n                '
                         '{% endif %}\r\n                "tag": "lark_md"\r\n            }\r\n        }\r\n    }\r\n}'),
        ('电话默认模板', '电话', '{}'),
    )

    def handle(self, *args, **options):
        for _ in self.alert_template_init:
            template_name, alert_mode_name, template_content = _
            alert_mode = AlertMode.objects.get(mode_name=alert_mode_name)
            alert_template, tag = AlertTemplate.objects.get_or_create(template_name=template_name, alert_mode=alert_mode)
            alert_template.template_content = template_content
            alert_template.save()
