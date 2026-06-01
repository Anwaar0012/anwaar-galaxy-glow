# services/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from services.models import ServiceCategory, Service

class Command(BaseCommand):
    help = 'Seed initial data for the website'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        # Create service categories
        categories_data = [
            {
                'name': 'AutoCAD Design',
                'slug': 'autocad-design',
                'icon': 'fas fa-cube',
                'description': 'Professional 2D/3D CAD design services',
                'order': 1
            },
            {
                'name': 'Adobe Creative Suite',
                'slug': 'adobe-creative-suite',
                'icon': 'fab fa-adobe',
                'description': 'Graphic design and photo editing',
                'order': 2
            },
            {
                'name': 'MS Office Solutions',
                'slug': 'ms-office-solutions',
                'icon': 'fab fa-microsoft',
                'description': 'Document, spreadsheet, and presentation services',
                'order': 3
            },
            {
                'name': 'Python Development',
                'slug': 'python-development',
                'icon': 'fab fa-python',
                'description': 'Custom Python applications and automation',
                'order': 4
            },
            {
                'name': 'Web Development',
                'slug': 'web-development',
                'icon': 'fas fa-code',
                'description': 'Django web applications',
                'order': 5
            },
            {
                'name': 'GUI Applications',
                'slug': 'gui-applications',
                'icon': 'fas fa-desktop',
                'description': 'PySide and Flet desktop/mobile apps',
                'order': 6
            },
        ]
        
        for cat_data in categories_data:
            category, created = ServiceCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')