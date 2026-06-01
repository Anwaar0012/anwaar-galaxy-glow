# projects/apps.py
from django.apps import AppConfig

class ProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'
    verbose_name = 'Projects Portfolio'
    
    def ready(self):
        # Import signals if you have them
        try:
            import projects.signals
        except ImportError:
            pass