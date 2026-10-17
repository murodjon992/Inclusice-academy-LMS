from django.apps import AppConfig


class InclusiveAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'inclusive_app'

    def ready(self):
        import inclusive_app.signals

