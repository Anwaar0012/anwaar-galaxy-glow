# services/apps.py
from django.apps import AppConfig

class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services'
    
    # def ready(self):
    #     # Don't import signals if it doesn't exist yet
    #     try:
    #         import services.signals
    #     except ImportError:
    #         pass