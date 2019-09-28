from django.apps import AppConfig

class OtherConfig(AppConfig):
    name = 'other'

    def ready(self):
        import other.notifications  # noqa: F401 pylint: disable=W0612, W0611, C0415
        import other.search_signals  # noqa: F401 pylint: disable=W0612, W0611, C0415
