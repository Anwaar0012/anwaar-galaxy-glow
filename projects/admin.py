# projects/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import ProjectCategory, Project, ProjectImage

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'icon', 'description')
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description', 'og_image'),
            'classes': ('collapse',),
        }),
    )

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'image_alt', 'caption', 'order']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'technologies', 'status', 'is_featured', 'completion_date', 'views_count']
    list_filter = ['status', 'is_featured', 'category', 'technologies', 'completion_date']
    search_fields = ['title', 'short_description', 'description', 'client', 'technologies']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'created_at', 'updated_at', 'image_preview']
    list_editable = ['status', 'is_featured']
    list_per_page = 20
    date_hierarchy = 'completion_date'
    
    inlines = [ProjectImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'client')
        }),
        ('Project Details', {
            'fields': ('short_description', 'description', 'technologies', 'other_technologies')
        }),
        ('Timeline', {
            'fields': ('start_date', 'completion_date', 'duration')
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_alt', 'image_preview', 'additional_images'),
            'description': 'Upload featured image (1200x600px recommended)'
        }),
        ('Links', {
            'fields': ('project_url', 'github_url', 'demo_video_url'),
            'classes': ('collapse',),
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description', 'focus_keyword'),
            'classes': ('collapse',),
            'description': 'Optimize this project for search engines'
        }),
        ('Status & Metadata', {
            'fields': ('status', 'is_featured', 'views', 'created_at', 'updated_at')
        }),
    )
    
    def views_count(self, obj):
        return format_html('<b>{}</b> views', obj.views)
    views_count.short_description = 'Views'
    views_count.admin_order_field = 'views'
    
    def image_preview(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.featured_image.url)
        return "No image"
    image_preview.short_description = 'Current Image'
    
    actions = ['make_published', 'make_featured', 'reset_views']
    
    def make_published(self, request, queryset):
        queryset.update(status='published')
    make_published.short_description = "Mark selected projects as published"
    
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
    make_featured.short_description = "Mark selected projects as featured"
    
    def reset_views(self, request, queryset):
        queryset.update(views=0)
    reset_views.short_description = "Reset view counts"

@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['project', 'image_alt', 'order', 'created_at']
    list_filter = ['project', 'created_at']
    search_fields = ['project__title', 'caption', 'image_alt']
    list_editable = ['order']