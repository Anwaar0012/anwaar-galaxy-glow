# type: ignore
from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.text import slugify

class ProjectCategory(models.Model):
    """Category for organizing projects"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-folder', 
                           help_text="Font Awesome icon class")
    
    # SEO Fields
    meta_title = models.CharField(max_length=60, blank=True, 
                                 help_text="SEO Title (60 chars max)")
    meta_description = models.CharField(max_length=160, blank=True, 
                                       help_text="SEO Description (160 chars max)")
    og_image = models.ImageField(upload_to='seo/categories/', null=True, blank=True,
                                help_text="Open Graph image for social sharing")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Project Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('projects:project_category', kwargs={'category_slug': self.slug})
    
    def save(self, *args, **kwargs):
        # Auto-generate meta title if not provided
        if not self.meta_title:
            self.meta_title = f"{self.name} Projects | Your Portfolio"
        super().save(*args, **kwargs)

class Project(models.Model):
    """Project model for portfolio items"""
    
    TECHNOLOGY_CHOICES = [
        ('python', 'Python'),
        ('django', 'Django'),
        ('flet', 'Flet'),
        ('pyside', 'PySide'),
        ('autocad', 'AutoCAD'),
        ('illustrator', 'Adobe Illustrator'),
        ('blender', 'Blender 3D'),
        ('photoshop', 'Adobe Photoshop'),
        ('office', 'MS Office'),
        ('web', 'Web Development'),
        ('mobile', 'Mobile App'),
        ('desktop', 'Desktop App'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, 
                                null=True, blank=True, related_name='projects')
    
    # Project Details
    short_description = models.CharField(max_length=300, blank=True)
    # description = RichTextField()
    description = CKEditor5Field(config_name='extends')  # or 'default'
    client = models.CharField(max_length=200, blank=True, help_text="Client name or company")
    technologies = models.CharField(max_length=50, choices=TECHNOLOGY_CHOICES, default='python')
    other_technologies = models.CharField(max_length=500, blank=True, 
                                         help_text="Comma separated list of additional technologies")
    
    # Timeline
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField()
    duration = models.CharField(max_length=100, default='1-2 weeks', 
                               help_text="e.g., 2 weeks, 1 month, 3 months")
    
    # Media
    featured_image = models.ImageField(upload_to='projects/featured/', 
                                      help_text="Main project image (1200x600px recommended)")
    featured_image_alt = models.CharField(max_length=125, blank=True, 
                                         help_text="Alt text for featured image (125 chars max)")
    additional_images = models.ImageField(upload_to='projects/gallery/', blank=True, null=True,
                                         help_text="Additional project images")
    
    # Links
    project_url = models.URLField(blank=True, help_text="Link to live project/demo")
    github_url = models.URLField(blank=True, help_text="Link to GitHub repository")
    demo_video_url = models.URLField(blank=True, help_text="Link to demo video")
    
    # SEO Fields
    meta_title = models.CharField(max_length=60, blank=True, 
                                 help_text="SEO Title (60 chars max)")
    meta_description = models.CharField(max_length=160, blank=True, 
                                       help_text="SEO Description (160 chars max)")
    focus_keyword = models.CharField(max_length=100, blank=True,
                                    help_text="Primary keyword for this project")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False, help_text="Featured on homepage")
    
    # Metadata
    views = models.PositiveIntegerField(default=0, editable=False)
    schema_markup = models.JSONField(null=True, blank=True, 
                                     help_text="JSON-LD schema markup for rich snippets")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-completion_date', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'is_featured']),
            models.Index(fields=['technologies']),
            models.Index(fields=['-completion_date']),
            models.Index(fields=['-views']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def get_technologies_list(self):
        """Return list of other technologies"""
        tech_list = []
        if self.other_technologies:
            tech_list = [tech.strip() for tech in self.other_technologies.split(',')]
        if self.technologies:
            tech_list.insert(0, self.get_technologies_display())
        return tech_list
    
    def save(self, *args, **kwargs):
        # Auto-generate meta title if not provided
        if not self.meta_title and self.title:
            self.meta_title = self.title[:57] + "..." if len(self.title) > 57 else self.title
        
        # Auto-generate meta description from short_description
        if not self.meta_description and self.short_description:
            self.meta_description = self.short_description[:157] + "..." if len(self.short_description) > 157 else self.short_description
        
        super().save(*args, **kwargs)

class ProjectImage(models.Model):
    """Additional images for project gallery"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='projects/gallery/')
    image_alt = models.CharField(max_length=125, blank=True, 
                                help_text="Alt text for image (125 chars max)")
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['project', 'order']),
        ]
    
    def __str__(self):
        return f"Image for {self.project.title}"