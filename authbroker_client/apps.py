from django.apps import AppConfig
from .logging import enable_logout_logging


class AuthbrokerClientConfig(AppConfig):
    name = "authbroker_client"

    def ready(self):
        enable_logout_logging()
