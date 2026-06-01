from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-folder')
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Note(models.Model):
    TYPE_CHOICES = [
        ('pdf', 'PDF Document'),
        ('doc', 'Word Document'),
        ('ppt', 'PowerPoint'),
        ('zip', 'Zip Archive'),
        ('link', 'External Link'),
        ('video', 'Video Tutorial'),
    ]
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    # Basic Info
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='notes')
    note_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='pdf')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    
    # File options
    file = models.FileField(upload_to='notes/files/', blank=True, null=True)
    file_size = models.CharField(max_length=20, blank=True)
    
    # Google Drive option (only the link - ID extracted automatically)
    google_drive_link = models.URLField(
        blank=True, 
        help_text="Paste Google Drive file link (e.g., https://drive.google.com/file/d/FILE_ID/view)"
    )
    
    # External links
    external_link = models.URLField(blank=True)
    download_link = models.URLField(blank=True)
    
    # Metadata
    author = models.CharField(max_length=100, blank=True)
    pages = models.IntegerField(default=0)
    is_free = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Stats
    download_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Calculate file size if file exists
        if self.file and not self.file_size:
            size = self.file.size
            if size < 1024 * 1024:
                self.file_size = f"{size/1024:.1f} KB"
            else:
                self.file_size = f"{size/(1024*1024):.1f} MB"
        
        super().save(*args, **kwargs)
    
    def get_google_drive_id(self):
        """Extract file ID from Google Drive URL"""
        if not self.google_drive_link:
            return ''
        
        if 'file/d/' in self.google_drive_link:
            parts = self.google_drive_link.split('file/d/')[1].split('/')
            return parts[0] if parts else ''
        elif 'id=' in self.google_drive_link:
            return self.google_drive_link.split('id=')[1].split('&')[0]
        return ''
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('downloads:note_detail', kwargs={'slug': self.slug})
    
    def get_download_url(self):
        if self.file:
            return self.file.url
        elif self.download_link:
            return self.download_link
        elif self.google_drive_link:
            return self.google_drive_link
        return '#'
    
    def get_icon(self):
        icons = {
            'pdf': 'fas fa-file-pdf',
            'doc': 'fas fa-file-word',
            'ppt': 'fas fa-file-powerpoint',
            'zip': 'fas fa-file-archive',
            'link': 'fas fa-link',
            'video': 'fas fa-video',
        }
        return icons.get(self.note_type, 'fas fa-file')
    
    def increment_download_count(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


class GoogleDriveFolder(models.Model):
    name = models.CharField(max_length=200)
    drive_link = models.URLField(
        help_text="Paste Google Drive folder URL (e.g., https://drive.google.com/drive/folders/FOLDER_ID)"
    )
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='drive_folders'
    )
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def folder_id(self):
        """Extract folder ID from Google Drive URL"""
        if not self.drive_link:
            return ''
        
        if 'folders/' in self.drive_link:
            return self.drive_link.split('folders/')[1].split('?')[0]
        elif 'id=' in self.drive_link:
            return self.drive_link.split('id=')[1].split('&')[0]
        return ''
    
    def get_embed_url(self):
        """Get embed URL for Google Drive folder"""
        if self.folder_id:
            return f"https://drive.google.com/embeddedfolderview?id={self.folder_id}#list"
        return self.drive_link