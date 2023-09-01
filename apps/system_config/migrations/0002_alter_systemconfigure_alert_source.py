# Generated by Django 4.2.2 on 2023-06-20 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerting', '0008_alertinhibition'),
        ('system_config', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemconfigure',
            name='alert_source',
            field=models.ManyToManyField(to='alerting.alertsource', verbose_name='需要提醒的告警源'),
        ),
    ]
