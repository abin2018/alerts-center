# Generated by Django 4.2.2 on 2023-06-18 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('on_call', '0002_oncallstuff_rank_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='OnCallTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence_name', models.CharField(default='on_call', max_length=50, verbose_name='序列名称')),
                ('sequence', models.JSONField(default={}, verbose_name='序列')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '值班表',
                'verbose_name_plural': '值班表',
            },
        ),
    ]
