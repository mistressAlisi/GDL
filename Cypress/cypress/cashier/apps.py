from django.apps import AppConfig


class CashierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cashier'

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals