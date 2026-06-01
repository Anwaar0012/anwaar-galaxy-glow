# type: ignore
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Project, ProjectCategory

class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Project.objects.filter(status='published')
        
        # Annotate with counts for performance
        queryset = queryset.select_related('category').prefetch_related('gallery_images')
        
        # Filter by technology
        technology = self.request.GET.get('technology')
        if technology and technology != 'all':
            queryset = queryset.filter(
                Q(technologies=technology) | 
                Q(other_technologies__icontains=technology)
            )
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(client__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(technologies__icontains=search_query) |
                Q(other_technologies__icontains=search_query)
            )
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get technology counts for filter
        tech_counts = {}
        for tech_code, tech_name in Project.TECHNOLOGY_CHOICES:
            count = Project.objects.filter(
                status='published',
                technologies=tech_code
            ).count()
            if count > 0:
                tech_counts[tech_code] = {
                    'name': tech_name,
                    'count': count
                }
        
        context['technologies'] = tech_counts
        context['categories'] = ProjectCategory.objects.annotate(
            project_count=Count('projects', filter=Q(projects__status='published'))
        ).filter(project_count__gt=0)
        
        # SEO Meta
        context['meta_title'] = "Portfolio Projects | Your Name"
        context['meta_description'] = "Explore our portfolio of web development, design, and software projects. See real-world examples of our work and expertise."
        
        return context

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Project.objects.filter(status='published').select_related('category')
    
    def get_object(self):
        obj = super().get_object()
        
        # Increment view count (only for non-staff)
        if not self.request.user.is_staff:
            obj.increment_views()
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Get related projects (same category or technology)
        related_projects = Project.objects.filter(
            status='published'
        ).exclude(
            id=project.id
        ).filter(
            Q(category=project.category) | 
            Q(technologies=project.technologies)
        ).select_related('category').distinct()[:4]
        
        context['related_projects'] = related_projects
        
        # Get previous and next projects for navigation
        context['prev_project'] = Project.objects.filter(
            status='published',
            completion_date__lt=project.completion_date
        ).order_by('-completion_date').first()
        
        context['next_project'] = Project.objects.filter(
            status='published',
            completion_date__gt=project.completion_date
        ).order_by('completion_date').first()
        
        # SEO Meta
        context['meta_title'] = project.meta_title or project.title
        context['meta_description'] = project.meta_description or project.short_description
        context['meta_keywords'] = project.focus_keyword
        context['og_image'] = project.featured_image.url if project.featured_image else None
        
        # Generate schema markup
        context['schema_markup'] = self.get_schema_markup(project)
        
        return context
    
    def get_schema_markup(self, project):
        """Generate JSON-LD schema markup for rich snippets"""
        schema = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": project.title,
            "description": project.short_description,
            "datePublished": project.completion_date.isoformat(),
            "dateModified": project.updated_at.isoformat(),
            "author": {
                "@type": "Person",
                "name": "Your Name"
            }
        }
        
        if project.featured_image:
            schema["image"] = project.featured_image.url
        
        if project.client:
            schema["about"] = f"Project for {project.client}"
        
        if project.technologies:
            schema["keywords"] = ", ".join(project.get_technologies_list())
        
        return schema

class ProjectCategoryView(ListView):
    model = Project
    template_name = 'projects/project_category.html'
    context_object_name = 'projects'
    paginate_by = 9
    
    def get_queryset(self):
        self.category = get_object_or_404(ProjectCategory, slug=self.kwargs['category_slug'])
        return Project.objects.filter(
            category=self.category,
            status='published'
        ).select_related('category').order_by('-is_featured', '-completion_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        
        # SEO Meta
        context['meta_title'] = self.category.meta_title or f"{self.category.name} Projects"
        context['meta_description'] = self.category.meta_description or f"Explore our {self.category.name} projects and portfolio examples."
        
        return context