# type: ignore
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Count
from django.http import HttpResponseRedirect, FileResponse, Http404
from django.urls import reverse
from django.contrib import messages
import os

from .models import Note, Category, GoogleDriveFolder
from .forms import NoteSearchForm

class NoteListView(ListView):
    model = Note
    template_name = 'downloads/note_list.html'
    context_object_name = 'notes'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Note.objects.filter(is_active=True).select_related('category')
        
        # Filter by category if specified
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        # Search functionality
        form = NoteSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            category = form.cleaned_data.get('category')
            level = form.cleaned_data.get('level')
            
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(short_description__icontains=query)
                )
            
            if category:
                queryset = queryset.filter(category=category)
            
            if level:
                queryset = queryset.filter(level=level)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(
            note_count=Count('notes')
        ).order_by('order', 'name')
        context['form'] = NoteSearchForm(self.request.GET)
        context['featured_notes'] = Note.objects.filter(
            is_featured=True, is_active=True
        )[:6]
        return context

class NoteDetailView(DetailView):
    model = Note
    template_name = 'downloads/note_detail.html'
    context_object_name = 'note'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_object(self):
        obj = super().get_object()
        obj.increment_view_count()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_notes'] = Note.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:4]
        context['drive_folders'] = GoogleDriveFolder.objects.filter(
            is_active=True
        ).order_by('order', 'name')
        return context

def download_note(request, slug):
    note = get_object_or_404(Note, slug=slug, is_active=True)
    
    # Check if user has permission (add premium checks here if needed)
    if not note.is_free and not request.user.is_authenticated:
        messages.warning(request, "Please login to download premium notes")
        return redirect(f"{reverse('downloads:note_detail', kwargs={'slug': slug})}?login=required")
    
    # Increment download count
    note.increment_download_count()
    
    # Redirect to appropriate download
    if note.file:
        # Serve file directly
        response = FileResponse(note.file.open(), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{note.title}{os.path.splitext(note.file.name)[1]}"'
        return response
    elif note.download_link:
        return redirect(note.download_link)
    elif note.google_drive_link:
        return redirect(note.google_drive_link)
    else:
        messages.error(request, "No download available for this note")
        return redirect('downloads:note_detail', slug=slug)

class GoogleDriveListView(TemplateView):
    template_name = 'downloads/drive_folders.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['folders'] = GoogleDriveFolder.objects.filter(
            is_active=True
        ).order_by('order', 'name')
        context['categories'] = Category.objects.annotate(
            note_count=Count('notes')
        ).order_by('order', 'name')
        return context