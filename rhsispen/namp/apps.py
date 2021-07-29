from django.apps import AppConfig

class NampConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'namp'

    def ready(self):
    	import namp.signals
