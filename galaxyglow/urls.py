from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import TemplateView
from services.views import HomeView
from blog.sitemaps import BlogPostSitemap, BlogCategorySitemap, BlogIndexSitemap

# Sitemaps configuration
sitemaps = {
    'blog_posts': BlogPostSitemap,
    'blog_categories': BlogCategorySitemap,
    'blog_index': BlogIndexSitemap,
}

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    
    # SEO - Better search engine visibility
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    
    # Main pages
    path('', HomeView.as_view(), name='home'),
    path('services/', include('services.urls')),
    path('projects/', include('projects.urls')),
    path('blog/', include('blog.urls')),
    path('testimonials/', include('testimonials.urls')),
    path('contact/', include('contact.urls')),
    path('downloads/', include('downloads.urls')),
]

# Serve media files in development only
# In production (Hostinger), static/media files are served by the web server
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)