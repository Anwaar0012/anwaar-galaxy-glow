# type: ignore
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.core.paginator import Paginator
from .models import Service, ServiceCategory
from typing import Optional

# Import other models here (at top, not inside method)
from projects.models import Project
from testimonials.models import Testimonial

class HomeView(TemplateView):
    """Home page view showing featured content"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured services
        context['featured_services'] = Service.objects.filter(is_featured=True)[:6]
        
        # Get featured projects
        context['featured_projects'] = Project.objects.filter(is_featured=True)[:4]
        
        # Get featured testimonials
        context['featured_testimonials'] = Testimonial.objects.filter(is_featured=True)[:3]
        
        # Add categories for navigation
        context['service_categories'] = ServiceCategory.objects.all()[:5]
        
        return context

class ServiceListView(ListView):
    """List all service categories with their services"""
    model = ServiceCategory
    template_name = 'services/service_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return ServiceCategory.objects.prefetch_related('services').all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_services'] = Service.objects.select_related('category').all()
        return context

class ServiceDetailView(DetailView):
    """Detailed view of a single service"""
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the current service
        service = self.object
        
        # Get related services from same category
        if service and service.category_id:  # Check if category exists
            context['related_services'] = Service.objects.filter(
                category_id=service.category_id  # Use ID for FK lookup
            ).exclude(
                pk=service.pk  # Use pk instead of id
            )[:3]
        else:
            context['related_services'] = Service.objects.none()
        
        return context

class CategoryDetailView(DetailView):
    """View services in a specific category"""
    model = ServiceCategory
    template_name = 'services/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add type hint
        category = self.object
        context['services'] = Service.objects.filter(category=category)
        return context