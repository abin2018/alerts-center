# Generated by Django 4.2.2 on 2023-06-18 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('on_call', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='oncallstuff',
            name='rank_number',
            field=models.SmallIntegerField(default=0, verbose_name='次序'),
        ),
    ]
