from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    # SEO Fields
    meta_title = models.CharField(max_length=60, blank=True, 
                                 help_text="SEO Title (60 chars max)")
    meta_description = models.CharField(max_length=160, blank=True, 
                                       help_text="SEO Description (160 chars max)")
    meta_keywords = models.CharField(max_length=200, blank=True,
                                    help_text="Comma-separated keywords")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:blog_category', kwargs={'category_slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = self.name
        if not self.meta_description and self.description:
            self.meta_description = self.description[:157] + "..." if len(self.description) > 157 else self.description
        super().save(*args, **kwargs)

class BlogPost(models.Model):
    TAGS = [
        ('python', 'Python'),
        ('django', 'Django'),
        ('autocad', 'AutoCAD'),
        ('design', 'Design'),
        ('tutorial', 'Tutorial'),
        ('tips', 'Tips & Tricks'),
        ('projects', 'Projects'),
        ('web-development', 'Web Development'),
        ('mobile-apps', 'Mobile Apps'),
        ('3d-modeling', '3D Modeling'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='posts')
    excerpt = models.TextField(max_length=300, help_text="Brief summary for blog listing")
    content = CKEditor5Field(config_name='extends')
    tags = models.CharField(max_length=100, choices=TAGS, default='tips')
    featured_image = models.ImageField(upload_to='blog/', help_text="1200x630px recommended for social sharing")
    featured_image_alt = models.CharField(max_length=125, blank=True, 
                                         help_text="Alt text for featured image")
    author = models.CharField(max_length=100, default='Anwaar')
    
    # SEO Fields
    meta_title = models.CharField(max_length=60, blank=True, 
                                 help_text="SEO Title (60 chars max)")
    meta_description = models.CharField(max_length=160, blank=True, 
                                       help_text="SEO Description (160 chars max)")
    meta_keywords = models.CharField(max_length=200, blank=True,
                                    help_text="Comma-separated keywords")
    canonical_url = models.URLField(blank=True, 
                                   help_text="Custom canonical URL if needed")
    
    # Social Media Fields
    og_title = models.CharField(max_length=60, blank=True, 
                               help_text="Facebook/Open Graph title")
    og_description = models.CharField(max_length=200, blank=True, 
                                     help_text="Facebook/Open Graph description")
    og_image = models.ImageField(upload_to='blog/og/', blank=True, null=True,
                                help_text="Custom image for social sharing")
    
    # Twitter Fields
    twitter_title = models.CharField(max_length=60, blank=True,
                                    help_text="Twitter card title")
    twitter_description = models.CharField(max_length=200, blank=True,
                                         help_text="Twitter card description")
    twitter_image = models.ImageField(upload_to='blog/twitter/', blank=True, null=True,
                                     help_text="Custom image for Twitter")
    
    # Schema Markup
    schema_markup = models.JSONField(null=True, blank=True,
                                    help_text="JSON-LD schema markup for rich snippets")
    
    # Status and Metadata
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0, editable=False)
    reading_time = models.PositiveIntegerField(default=5, help_text="Estimated reading time in minutes")
    allow_comments = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_published', 'is_featured']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['tags']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:blog_detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])
    
    def save(self, *args, **kwargs):
        # Auto-generate SEO fields if not provided
        if not self.meta_title:
            self.meta_title = self.title[:57] + "..." if len(self.title) > 57 else self.title
        
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:157] + "..." if len(self.excerpt) > 157 else self.excerpt
        
        if not self.featured_image_alt and self.title:
            self.featured_image_alt = self.title[:120]
        
        # Auto-calculate reading time if not set
        if not self.reading_time and self.content:
            word_count = len(self.content.split())
            self.reading_time = max(1, round(word_count / 200))  # 200 words per minute
        
        super().save(*args, **kwargs)