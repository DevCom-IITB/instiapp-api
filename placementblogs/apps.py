from django.apps import AppConfig

class PlacementBlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'placementblogs'

    def ready(self):
        import placementblogs.signals