# downloads/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Note, GoogleDriveFolder

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'note_count']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']
    
    def note_count(self, obj):
        return obj.notes.count()
    note_count.short_description = 'Number of Notes'

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'note_type', 'level', 'is_free', 'is_featured', 'download_count', 'created_at']
    list_filter = ['category', 'note_type', 'level', 'is_free', 'is_featured', 'is_active']
    search_fields = ['title', 'description', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['download_count', 'view_count', 'created_at', 'updated_at']
    list_editable = ['is_free', 'is_featured']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'category', 'is_active')
        }),
        ('File Information', {
            'fields': ('note_type', 'file', 'google_drive_link', 'download_link')
        }),
        ('Metadata', {
            'fields': ('author', 'pages', 'level', 'is_free', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('download_count', 'view_count', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Auto-extract Google Drive ID if needed (optional)
        if obj.google_drive_link and not obj.get_google_drive_id():
            # Just save, the ID will be extracted on the fly
            pass
        super().save_model(request, obj, form, change)


@admin.register(GoogleDriveFolder)
class GoogleDriveFolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'order', 'folder_id_display']
    list_filter = ['category', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['folder_id_display']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'drive_link', 'description', 'category', 'is_active', 'order')
        }),
        ('Google Drive Info', {
            'fields': ('folder_id_display',),
            'classes': ('collapse',)
        }),
    )
    
    def folder_id_display(self, obj):
        """Display extracted folder ID"""
        if obj.folder_id:
            return format_html(
                '<code>{}</code> <span style="color: green;">✓ Auto-extracted from link</span>',
                obj.folder_id
            )
        return "No folder ID found in link"
    folder_id_display.short_description = 'Folder ID (Auto)'
    
    def save_model(self, request, obj, form, change):
        # Validate that the drive_link contains a folder ID
        if obj.drive_link and not obj.folder_id:
            from django.contrib import messages
            messages.warning(
                request, 
                'The Google Drive link does not appear to contain a valid folder ID. '
                'Make sure you\'re using a folder link (contains "folders/" or "id=").'
            )
        super().save_model(request, obj, form, change)