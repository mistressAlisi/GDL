from django.apps import AppConfig

class GraderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'grader'

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        # from . import receivers
        # print("Imported Receivers")
        #
        # from matches.signals import signal_match_final
        # signal_match_final.connect(receivers.match_signal_match_final_handler,dispatch_uid="signal_match_final_handler")
        pass
