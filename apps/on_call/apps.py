from django.apps import AppConfig


class OnCallConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.on_call'
    verbose_name = '值班信息'

    def ready(self):
        import apps.on_call.signals.handlers


