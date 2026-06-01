# type: ignore
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import Manager

class ServiceCategory(models.Model):
    name: models.CharField = models.CharField(max_length=100)
    slug: models.SlugField = models.SlugField(unique=True)
    icon: models.CharField = models.CharField(max_length=50, help_text="Font Awesome icon class")
    description: models.TextField = models.TextField()
    order: models.IntegerField = models.IntegerField(default=0)
    
    # SEO Fields
    meta_title: models.CharField = models.CharField(max_length=60, blank=True, help_text="SEO Title (60 chars max)")
    meta_description: models.CharField = models.CharField(max_length=160, blank=True, help_text="SEO Description (160 chars max)")
    og_image: models.ImageField = models.ImageField(upload_to='seo/', null=True, blank=True, help_text="Open Graph image")
    
    objects: 'Manager[ServiceCategory]'
    
    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['order']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self) -> str:
        return self.name
    
    def get_absolute_url(self) -> str:
        return reverse('services:category_detail', args=[self.slug])
    
    @property
    def service_count(self):
        """Return number of services in this category"""
        return self.services.count()

class Service(models.Model):
    SERVICE_TYPES: list[tuple[str, str]] = [
        ('basic', 'Basic Package'),
        ('standard', 'Standard Package'),
        ('premium', 'Premium Package'),
    ]
    
    category: models.ForeignKey = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name: models.CharField = models.CharField(max_length=200)
    slug: models.SlugField = models.SlugField(unique=True)
    short_description: models.TextField = models.TextField()
    detailed_description: CKEditor5Field = CKEditor5Field(config_name='extends')
    service_type: models.CharField = models.CharField(max_length=20, choices=SERVICE_TYPES, default='standard')
    price: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    duration: models.CharField = models.CharField(max_length=50, help_text="e.g., 3-5 days, 1 week")
    features: CKEditor5Field = CKEditor5Field(config_name='extends', help_text="List features with bullet points")
    image: models.ImageField = models.ImageField(upload_to='services/', null=True, blank=True)
    is_featured: models.BooleanField = models.BooleanField(default=False)
    order: models.IntegerField = models.IntegerField(default=0)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    
    # SEO Fields
    meta_title: models.CharField = models.CharField(max_length=60, blank=True, help_text="SEO Title (60 chars max)")
    meta_description: models.CharField = models.CharField(max_length=160, blank=True, help_text="SEO Description (160 chars max)")
    
    objects: 'Manager[Service]'
    
    # Django automatically adds this, but type hint it for Pylance
    category_id: int
    
    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['category', 'is_featured']),
        ]
    
    def __str__(self) -> str:
        return f"{self.name}  ({self.service_type})"
    
    def get_absolute_url(self) -> str:
        return reverse('services:service_detail', args=[self.slug])