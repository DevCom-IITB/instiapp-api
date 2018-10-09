from django.apps import AppConfig

class OtherConfig(AppConfig):
    name = 'other'

    def ready(self):
        import other.notifications  # noqa: F401 pylint: disable=W0612
