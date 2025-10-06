# community/apps.py

from django.apps import AppConfig

class CommunityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' # Recommended for modern Django
    name = 'community'

    def ready(self):
        """
        This method is called when the app is ready.
        Importing signals here ensures they are connected.
        """
        import community.signal