# contact/models.py
from django.db import models

class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('closed', 'Closed'),
    ]
    
    SERVICE_CHOICES = [
        ('autocad', 'AutoCAD Design'),
        ('illustrator', 'Illustrator Design'),
        ('blender', '3D Modeling with Blender'),
        ('photoshop', 'Photo Editing'),
        ('office', 'MS Office Projects'),
        ('python', 'Python Development'),
        ('django', 'Django Web Development'),
        ('flet', 'Flet App Development'),
        ('pyside', 'PySide GUI Development'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
