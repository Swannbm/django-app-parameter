from django.apps import AppConfig


class DjangoAppParameterConfig(AppConfig):
    default_auto_field: str = "django.db.models.BigAutoField"
    name = "django_app_parameter"
