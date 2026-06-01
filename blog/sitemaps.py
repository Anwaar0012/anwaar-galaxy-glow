# type: ignore
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost, BlogCategory

class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'
    
    def items(self):
        return BlogPost.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return reverse('blog:blog_detail', args=[obj.slug])

class BlogCategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    protocol = 'https'
    
    def items(self):
        return BlogCategory.objects.all()
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return reverse('blog:blog_category', args=[obj.slug])

class BlogIndexSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    protocol = 'https'
    
    def items(self):
        return ['blog:blog_list']
    
    def location(self, item):
        return reverse(item)