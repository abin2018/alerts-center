from apps.system_config.models import SystemConfigure
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            system_configure = SystemConfigure.objects.get(configure_name='默认配置')
        except SystemConfigure.DoesNotExist:
            system_configure = SystemConfigure(configure_name='默认配置')
        system_configure.save()
