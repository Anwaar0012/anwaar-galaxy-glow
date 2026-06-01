# type: ignore
from django.db import models
from django.utils import timezone
from django.urls import reverse

class Testimonial(models.Model):
    RATINGS = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Client Information
    client_name = models.CharField(max_length=200, verbose_name="Full Name")
    client_email = models.EmailField(blank=True, verbose_name="Email Address", 
                                     help_text="Not shown publicly - for verification only")
    client_role = models.CharField(max_length=200, blank=True, verbose_name="Job Title/Role")
    company = models.CharField(max_length=200, blank=True, verbose_name="Company Name")
    location = models.CharField(max_length=200, blank=True, verbose_name="Location", 
                                help_text="e.g., New York, USA")
    
    # Testimonial Content
    testimonial = models.TextField(verbose_name="Your Testimonial")
    testimonial_short = models.CharField(max_length=150, blank=True, 
                                         verbose_name="Short Version", 
                                         help_text="Auto-generated from full testimonial")
    rating = models.IntegerField(choices=RATINGS, default=5, verbose_name="Rating")
    project = models.CharField(max_length=200, blank=True, verbose_name="Related Project/Service/Blog", 
                               help_text="Optional: Name of the related project, service, or blog post you're reviewing")
    
    # Media
    client_image = models.ImageField(upload_to='testimonials/', blank=True, null=True, 
                                     verbose_name="Client Photo", 
                                     help_text="Optional: Your photo (will be displayed publicly)")
    client_image_alt = models.CharField(max_length=125, blank=True, 
                                        verbose_name="Photo Alt Text")
    
    # Meta & Status
    is_featured = models.BooleanField(default=False, db_index=True, 
                                      verbose_name="Featured", 
                                      help_text="Show in featured section")
    is_verified = models.BooleanField(default=False, 
                                      verbose_name="Verified Client", 
                                      help_text="Mark if we've confirmed this is a real client")
    is_active = models.BooleanField(default=True, db_index=True, 
                                    verbose_name="Active", 
                                    help_text="Show on website")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending',
                             db_index=True, verbose_name="Approval Status")
    
    # Administrative
    admin_notes = models.TextField(blank=True, verbose_name="Admin Notes", 
                                   help_text="Internal notes only")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Approved Date")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Submitted Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    
    class Meta:
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"{self.client_name} - {self.rating}★ ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Auto-generate short testimonial
        if not self.testimonial_short and self.testimonial:
            self.testimonial_short = self.testimonial[:147] + "..." if len(self.testimonial) > 147 else self.testimonial
        
        # Auto-generate image alt text
        if not self.client_image_alt and self.client_name:
            self.client_image_alt = f"{self.client_name} - Client Testimonial"
        
        # Set approved date when status changes to approved
        if self.status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('testimonials:detail', kwargs={'pk': self.pk})
    
    @property
    def display_rating_stars(self):
        """Return HTML for star rating"""
        full_stars = int(self.rating)
        empty_stars = 5 - full_stars
        return '★' * full_stars + '☆' * empty_stars