from django import forms
from django.utils.safestring import mark_safe
import jinja2
import json


class AlertTargetForm(forms.ModelForm):
    target_content = forms.CharField(required=True, label='对象地址',
                                     widget=forms.TextInput(attrs={"style": "width:800px;"}))


class AlertRulesForm(forms.ModelForm):
    rule_name = forms.CharField(required=True, label='规则名称',
                                widget=forms.TextInput(attrs={"style": "width:600px;"}))
    alert_object = forms.CharField(required=False, label='告警对象',
                                   widget=forms.TextInput(attrs={"style": "width:600px;"}))
    alert_object_ip = forms.CharField(required=True, label='告警对象IP',
                                      widget=forms.TextInput(attrs={"style": "width:600px;", "value": "0.0.0.0"}))
    alert_object_groups = forms.CharField(required=False, label='告警对象属组',
                                          widget=forms.TextInput(attrs={"style": "width:600px;"}))
    alert_content = forms.CharField(required=False, label='告警内容(关键字)',
                                    widget=forms.TextInput(attrs={"style": "width:600px;"}))
    monitor_template = forms.CharField(required=False, label='监控模板',
                                       widget=forms.TextInput(attrs={"style": "width:600px;"}))
    # alert_object_label = forms.JSONField(required=False, label='告警对象标签',
    #                                      widget=forms.(attrs={"style": "width:600px;"}))


class AlertInhibitionForm(forms.ModelForm):
    alert_object = forms.CharField(required=False, label='告警对象',
                                   widget=forms.TextInput(attrs={"style": "width:600px;"}))
    alert_object_ip = forms.CharField(required=False, label='维护对象IP',
                                      widget=forms.TextInput(attrs={"style": "width:600px;"}))
    # alert_content_keyword = forms.JSONField(required=False, label='告警内容(关键词)',
    #                                         widget=forms.Textarea(attrs={"style": "width:600px;"}))


class AlertTemplateForm(forms.ModelForm):
    template_content = forms.CharField(required=True, label='告警内容模板',
                                       widget=forms.Textarea(attrs={"style": "width:1500px;height:300px"}),
                                       help_text=mark_safe('jinja2模板格式，支持的变量有：<ul>'
                                                           '<li>告警源ID：{{ alert_source }}</li>'
                                                           '<li>告警源名称：{{ alert_source_name }}</li>'
                                                           '<li>告警ID：{{ alert_id }}</li>'
                                                           '<li>告警内容：{{ alert_content }}</li>'
                                                           '<li>告警级别：{{ alert_level }}</li>'
                                                           '<li>告警状态：{{ alert_status }}</li>'
                                                           '<li>告警对象：{{ alert_object }}</li>'
                                                           '<li>告警对象IP：{{ alert_object_ip }}</li>'
                                                           '<li>告警对象属组：{{ alert_object_groups }}</li>'
                                                           '<li>监控值：{{ latest_value }}</li>'
                                                           '<li>触发时间：{{ event_time }}</li>'
                                                           '<li>恢复时间：{{ event_time }}</li>'
                                                           '<li>分配角色：{{ role }}</li>'
                                                           '<li>分配人员：{{ assigned_stuff }}</li>'
                                                           '</ul>'))

    def clean(self):
        clean_data = super().clean()
        template_content = clean_data.get('template_content')
        try:
            _templates = jinja2.Template(template_content)
        except Exception as e:
            raise forms.ValidationError("告警内容模板jinja2读取失败: \n第{}行, 错误信息:{}".format(e.lineno, e.message))
        else:
            alert_mode = clean_data["alert_mode"]
            try:
                renderer_templates = json.loads(_templates.render())
            except Exception as e:
                raise forms.ValidationError('json解析失败:{}'.format(e))
            if not isinstance(renderer_templates, dict):
                raise forms.ValidationError('应解析为字典')
            if alert_mode.mode_name == '邮箱':
                if not renderer_templates.get('subject') or not renderer_templates.get('message'):
                    raise forms.ValidationError('邮箱模板应至少包含subject和message字段')
        return clean_data
