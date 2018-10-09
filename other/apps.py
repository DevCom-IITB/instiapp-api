from django.apps import AppConfig

class OtherConfig(AppConfig):
    name = 'other'

    def ready(self):
        import other.notifications  # pylint: disable=W0612 # noqa: F401
