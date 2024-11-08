from django.apps import AppConfig

class HbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hb'
    verbose_name='管理系统'

    def ready(self):
        import hb.signals
