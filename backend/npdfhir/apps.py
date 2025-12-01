from django.apps import AppConfig


class NPDFHIRConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "npdfhir"

    def ready(self):
        # Import signals module to connect the handlers
        pass
