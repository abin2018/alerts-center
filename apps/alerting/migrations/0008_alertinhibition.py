# Generated by Django 4.2.2 on 2023-06-19 12:16

import apps.alerting.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerting', '0007_alter_alertrules_alert_content_operator_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertInhibition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30, verbose_name='标题')),
                ('inhibition_start_datetime', models.DateTimeField(verbose_name='抑制开始时间')),
                ('inhibition_end_datetime', models.DateTimeField(verbose_name='抑制终止时间')),
                ('alert_object', models.JSONField(blank=True, default=list, verbose_name='告警对象')),
                ('alert_object_ip', models.CharField(blank=True, help_text='写法:192.168.1.1或192.168.1.1,192.168.1.2或192.168.1.1-5或192.168.1.0/32或192.168.1.1|3|5', max_length=200, verbose_name='维护对象IP')),
                ('alert_content_keyword', models.JSONField(blank=True, default=apps.alerting.models.gen_alert_content_keyword, verbose_name='告警内容(关键词)')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('alert_source', models.ManyToManyField(related_name='alert_inhibition', to='alerting.alertsource', verbose_name='告警源')),
            ],
            options={
                'verbose_name': '告警抑制',
                'verbose_name_plural': '告警抑制',
            },
        ),
    ]
