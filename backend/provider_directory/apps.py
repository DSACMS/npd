from django.apps import AppConfig


class ProviderDirectoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "provider_directory"

    def ready(self):
        from . import flag_conditions as flag_conditions
