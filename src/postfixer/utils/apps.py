from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "postfixer.utils"

    def ready(self):
        from . import checks  # noqa
