# type: ignore
from typing import Optional, cast, Any
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.core.paginator import Paginator
from django.urls import reverse
from .models import Service, ServiceCategory

# Import other models here (at top, not inside method)
from projects.models import Project
from testimonials.models import Testimonial

class HomeView(TemplateView):
    """Home page view showing featured content"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
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
    
    def get_queryset(self) -> Any:
        return ServiceCategory.objects.prefetch_related('services').all()
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
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
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        # Get the current service
        service = self.get_object()
        
        # Get related services from same category using category object directly
        if hasattr(service, 'category') and service.category:
            context['related_services'] = Service.objects.filter(
                category=service.category  # Use the category object instead of category_id
            ).exclude(
                pk=service.pk
            )[:3]
        else:
            context['related_services'] = Service.objects.none()
        
        # Prepare WhatsApp message for ordering
        # This creates a pre-filled message that will be URL-encoded in the template
        whatsapp_message = f"""Hi! I'm interested in ordering your {service.name} service.

Service Details:
- Name: {service.name}
- Price: ${service.price if service.price else 'Contact for price'}
- Category: {service.category.name if service.category else 'N/A'}

Please let me know the next steps to proceed.
I can pay via Sadapay or other available methods.

Thank you!"""
        
        context['whatsapp_message'] = whatsapp_message
        
        return context

class CategoryDetailView(DetailView):
    """View services in a specific category"""
    model = ServiceCategory
    template_name = 'services/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        # Get the category object
        category = self.get_object()
        context['services'] = Service.objects.filter(category=category)
        
        # Optional: Add related categories (excluding current)
        context['related_categories'] = ServiceCategory.objects.exclude(
            pk=category.pk
        )[:4]
        
        return context