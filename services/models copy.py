from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    description = models.TextField()
    order = models.IntegerField(default=0)
    
    # SEO Fields
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO Title (60 chars max)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO Description (160 chars max)")
    og_image = models.ImageField(upload_to='seo/', null=True, blank=True, help_text="Open Graph image")
    
    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['order']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('services:category_detail', args=[self.slug])

class Service(models.Model):
    SERVICE_TYPES = [
        ('basic', 'Basic Package'),
        ('standard', 'Standard Package'),
        ('premium', 'Premium Package'),
    ]
    
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    detailed_description = CKEditor5Field(config_name='extends')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, default='standard')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, help_text="e.g., 3-5 days, 1 week")
    features = CKEditor5Field(config_name='extends', help_text="List features with bullet points")
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO Fields
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO Title (60 chars max)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO Description (160 chars max)")
    
    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['category', 'is_featured']),
        ]
    
    def __str__(self):
        # return f"{self.name} - {self.get_service_type_display()}"
        return f"{self.name}  ({self.service_type})"
    
    def get_absolute_url(self):
        return reverse('services:service_detail', args=[self.slug])
