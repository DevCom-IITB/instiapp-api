from django.apps import AppConfig


class CalendarhubConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calendarhub'
    
    def ready(self):
        from calendarhub.tasks import signals  # noqa: F401