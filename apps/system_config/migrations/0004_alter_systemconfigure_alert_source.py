# Generated by Django 4.2.2 on 2023-06-20 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerting', '0009_alter_alertcontent_alert_source'),
        ('system_config', '0003_alter_systemconfigure_alert_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemconfigure',
            name='alert_source',
            field=models.ManyToManyField(blank=True, to='alerting.alertsource', verbose_name='需要提醒的告警源'),
        ),
    ]
