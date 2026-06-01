# type: ignore
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Avg, Q
from django.core.cache import cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from .models import Testimonial
from .forms import TestimonialForm

class TestimonialListView(ListView):
    model = Testimonial
    template_name = 'testimonials/testimonial_list.html'
    context_object_name = 'testimonials'
    paginate_by = 9
    
    def get_queryset(self):
        # Only show approved testimonials
        queryset = Testimonial.objects.filter(
            is_active=True,
            status='approved'
        ).select_related()
        
        # Filter by rating
        rating = self.request.GET.get('rating')
        if rating and rating.isdigit():
            queryset = queryset.filter(rating=int(rating))
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(client_name__icontains=search_query) |
                Q(testimonial__icontains=search_query) |
                Q(company__icontains=search_query) |
                Q(project__icontains=search_query)
            )
        
        return queryset.order_by('-is_featured', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get statistics with caching
        stats_cache_key = 'testimonial_stats_v2'
        stats = cache.get(stats_cache_key)
        
        if not stats:
            stats = Testimonial.objects.filter(
                is_active=True, 
                status='approved'
            ).aggregate(
                total_count=Count('id'),
                average_rating=Avg('rating')
            )
            stats['five_star_count'] = Testimonial.objects.filter(
                is_active=True, status='approved', rating=5
            ).count()
            cache.set(stats_cache_key, stats, 3600)
        
        context.update(stats)
        
        # Get featured testimonials
        featured_cache_key = 'featured_testimonials_v2'
        featured = cache.get(featured_cache_key)
        
        if not featured:
            featured = Testimonial.objects.filter(
                is_active=True,
                status='approved',
                is_featured=True
            )[:4]
            cache.set(featured_cache_key, featured, 1800)
        
        context['featured_testimonials'] = featured
        
        # Get recent testimonials
        context['recent_testimonials'] = Testimonial.objects.filter(
            is_active=True, status='approved'
        )[:6]
        
        # Get rating breakdown
        rating_breakdown = []
        for rating in range(5, 0, -1):
            count = Testimonial.objects.filter(
                is_active=True, status='approved', rating=rating
            ).count()
            percentage = (count / context['total_count'] * 100) if context['total_count'] > 0 else 0
            rating_breakdown.append({
                'stars': rating,
                'count': count,
                'percentage': round(percentage)
            })
        context['rating_breakdown'] = rating_breakdown
        
        # Get common projects
        context['common_projects'] = Testimonial.objects.filter(
            is_active=True, status='approved'
        ).exclude(
            project=''
        ).values('project').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return context

class TestimonialSubmitView(CreateView):
    model = Testimonial
    form_class = TestimonialForm
    template_name = 'testimonials/testimonial_form.html'
    success_url = reverse_lazy('testimonials:thank_you')
    
    def form_valid(self, form):
        testimonial = form.save(commit=False)
        testimonial.status = 'pending'
        testimonial.is_active = False  # Will be activated upon approval
        
        # Save the testimonial
        testimonial.save()
        
        # Send notification email to admin
        if settings.DEBUG:
            print(f"New testimonial submitted by {testimonial.client_name}")
        else:
            try:
                send_mail(
                    subject=f'New Testimonial Submitted - {testimonial.client_name}',
                    message=f"""
                    A new testimonial has been submitted:
                    
                    Client: {testimonial.client_name}
                    Email: {testimonial.client_email}
                    Rating: {testimonial.rating} stars
                    
                    Testimonial:
                    {testimonial.testimonial}
                    
                    Admin URL: /admin/testimonials/testimonial/{testimonial.id}/change/
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
            except:
                pass
        
        messages.success(
            self.request, 
            'Thank you for your testimonial! It will be reviewed and published soon.'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Share Your Experience'
        context['subtitle'] = 'We value your feedback and would love to hear about your journey with us'
        return context

class TestimonialThankYouView(TemplateView):
    template_name = 'testimonials/thank_you.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_testimonials'] = Testimonial.objects.filter(
            is_active=True, status='approved'
        )[:3]
        return context

class TestimonialDetailView(DetailView):
    model = Testimonial
    template_name = 'testimonials/testimonial_detail.html'
    context_object_name = 'testimonial'
    
    def get_queryset(self):
        return Testimonial.objects.filter(is_active=True, status='approved')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['other_testimonials'] = Testimonial.objects.filter(
            is_active=True, status='approved'
        ).exclude(
            id=self.object.id
        )[:3]
        return context

class TestimonialAdminPendingListView(LoginRequiredMixin, ListView):
    """Admin view to manage pending testimonials (requires login)"""
    model = Testimonial
    template_name = 'admin/testimonials/pending_list.html'
    context_object_name = 'pending_testimonials'
    paginate_by = 20
    
    def get_queryset(self):
        return Testimonial.objects.filter(status='pending').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_pending'] = Testimonial.objects.filter(status='pending').count()
        context['total_approved'] = Testimonial.objects.filter(status='approved').count()
        context['total_rejected'] = Testimonial.objects.filter(status='rejected').count()
        return context