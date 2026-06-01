# type: ignore
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Project, ProjectCategory

class ProjectSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        return Project.objects.filter(status='published').select_related('category')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()

class ProjectCategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    
    def items(self):
        return ProjectCategory.objects.all()
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()