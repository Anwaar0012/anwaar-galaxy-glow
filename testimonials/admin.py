# testimonials/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from .models import Testimonial
from .forms import TestimonialAdminForm

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    form = TestimonialAdminForm
    list_display = [
        'client_name', 'rating_stars_display', 'project', 
        'status_badge', 'is_featured', 'created_at'
    ]
    list_filter = ['status', 'rating', 'is_featured', 'is_verified', 'created_at']
    search_fields = ['client_name', 'client_email', 'company', 'testimonial', 'project']
    readonly_fields = ['created_at', 'updated_at', 'approved_at', 'short_testimonial_preview']
    list_editable = ['is_featured']
    list_per_page = 20
    
    fieldsets = (
        ('Client Information', {
            'fields': ('client_name', 'client_email', 'client_role', 'company', 'location')
        }),
        ('Testimonial Content', {
            'fields': ('testimonial', 'short_testimonial_preview', 'rating', 'project')
        }),
        ('Media', {
            'fields': ('client_image', 'client_image_alt'),
            'classes': ('collapse',)
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_active', 'is_featured', 'is_verified', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'approved_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_testimonials', 'feature_testimonials', 'mark_as_verified']
    
    def rating_stars_display(self, obj):
        """Display rating as stars"""
        full_stars = obj.rating
        empty_stars = 5 - full_stars
        stars = '★' * full_stars + '☆' * empty_stars
        return format_html('<span style="color: #ffc107; font-size: 1.2em;">{}</span>', stars)
    rating_stars_display.short_description = 'Rating'
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'pending': '#ff9800',
            'approved': '#4caf50',
            'rejected': '#f44336'
        }
        color = colors.get(obj.status, '#9e9e9e')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.8em;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def short_testimonial_preview(self, obj):
        """Show preview of testimonial"""
        return obj.testimonial[:200] + '...' if len(obj.testimonial) > 200 else obj.testimonial
    short_testimonial_preview.short_description = 'Testimonial Preview'
    
    def approve_testimonials(self, request, queryset):
        """Approve selected testimonials"""
        updated = queryset.update(status='approved', is_active=True, approved_at=timezone.now())
        self.message_user(request, f'{updated} testimonials were approved successfully.')
    approve_testimonials.short_description = 'Approve selected testimonials'
    
    def feature_testimonials(self, request, queryset):
        """Mark selected testimonials as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} testimonials marked as featured.')
    feature_testimonials.short_description = 'Mark as featured'
    
    def mark_as_verified(self, request, queryset):
        """Mark selected testimonials as verified"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} testimonials marked as verified.')
    mark_as_verified.short_description = 'Mark as verified'
    
    def save_model(self, request, obj, form, change):
        """Auto-set approved date when status changes to approved"""
        if obj.status == 'approved' and not obj.approved_at:
            obj.approved_at = timezone.now()
        super().save_model(request, obj, form, change)