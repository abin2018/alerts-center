# Generated by Django 4.2.2 on 2023-06-18 06:10

import apps.meta_info.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta_info', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='alertmode',
            name='additional_attrs',
            field=models.JSONField(default=apps.meta_info.models.gen_additional_attrs, verbose_name='附加属性'),
        ),
    ]
