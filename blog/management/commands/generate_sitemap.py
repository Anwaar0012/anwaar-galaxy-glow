# blog/management/commands/generate_sitemap.py
from django.core.management.base import BaseCommand
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.test import Client

class Command(BaseCommand):
    help = 'Generate sitemap.xml file'

    def handle(self, *args, **options):
        client = Client()
        response = client.get('/sitemap.xml')
        
        with open('sitemap.xml', 'wb') as f:
            f.write(response.content)
        
        self.stdout.write(self.style.SUCCESS('Successfully generated sitemap.xml'))