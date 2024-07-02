from django.apps import AppConfig
import os

class IdihaumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'idihaum'

    def ready(self):
        if os.environ.get('RUN_MAIN', False):
            from . import mqtt
            mqtt.initialize_mqtt()
