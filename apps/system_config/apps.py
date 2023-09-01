from django.apps import AppConfig


class SystemConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.system_config'
    verbose_name = '系统配置'

    def ready(self):
        import apps.system_config.signals.handlers
