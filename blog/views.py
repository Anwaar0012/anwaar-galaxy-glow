# type: ignore
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import BlogPost, BlogCategory

class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(tags__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Filter by tag
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags=tag)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        return queryset.select_related('category').prefetch_related().order_by('-is_featured', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get categories with post counts
        context['categories'] = BlogCategory.objects.annotate(
            post_count=Count('posts', filter=Q(posts__is_published=True))
        ).filter(post_count__gt=0)
        
        # Get all available tags with counts
        tag_counts = []
        for tag_code, tag_name in BlogPost.TAGS:
            count = BlogPost.objects.filter(is_published=True, tags=tag_code).count()
            if count > 0:
                tag_counts.append({
                    'code': tag_code,
                    'name': tag_name,
                    'count': count
                })
        context['blog_tags'] = tag_counts
        
        # Featured posts
        context['featured_posts'] = BlogPost.objects.filter(
            is_published=True,
            is_featured=True
        ).select_related('category')[:3]
        
        # Popular posts (by views in last 30 days)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        context['popular_posts'] = BlogPost.objects.filter(
            is_published=True,
            created_at__gte=thirty_days_ago
        ).order_by('-views')[:5]
        
        # SEO Meta
        context['meta_title'] = "Blog | Anwaar Galaxy Glow"
        context['meta_description'] = "Explore our latest articles, tutorials, and insights about web development, design, and technology."
        context['canonical_url'] = self.request.build_absolute_uri()
        
        return context

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).select_related('category')
    
    def get_object(self):
        obj = super().get_object()
        
        # Increment view count (only for non-staff)
        if not self.request.user.is_staff:
            obj.increment_views()
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Get previous and next posts
        context['previous_post'] = BlogPost.objects.filter(
            is_published=True,
            created_at__lt=post.created_at
        ).order_by('-created_at').first()
        
        context['next_post'] = BlogPost.objects.filter(
            is_published=True,
            created_at__gt=post.created_at
        ).order_by('created_at').first()
        
        # Get related posts (same category or tags)
        context['related_posts'] = BlogPost.objects.filter(
            is_published=True
        ).exclude(
            id=post.id
        ).filter(
            Q(category=post.category) | Q(tags=post.tags)
        ).select_related('category')[:3]
        
        # Get categories for sidebar
        context['categories'] = BlogCategory.objects.annotate(
            post_count=Count('posts', filter=Q(posts__is_published=True))
        ).filter(post_count__gt=0)
        
        # SEO Meta
        context['meta_title'] = post.meta_title or post.title
        context['meta_description'] = post.meta_description or post.excerpt
        context['meta_keywords'] = post.meta_keywords or f"{post.tags}, {post.category.name if post.category else ''}"
        context['canonical_url'] = post.canonical_url or self.request.build_absolute_uri()
        
        # Open Graph tags
        context['og_title'] = post.og_title or post.meta_title or post.title
        context['og_description'] = post.og_description or post.meta_description or post.excerpt
        context['og_image'] = post.og_image.url if post.og_image else post.featured_image.url if post.featured_image else None
        context['og_url'] = self.request.build_absolute_uri()
        context['og_type'] = 'article'
        
        # Twitter Card tags
        context['twitter_title'] = post.twitter_title or context['og_title']
        context['twitter_description'] = post.twitter_description or context['og_description']
        context['twitter_image'] = post.twitter_image.url if post.twitter_image else context['og_image']
        context['twitter_card'] = 'summary_large_image' if context['twitter_image'] else 'summary'
        
        # Article schema
        context['schema_markup'] = post.schema_markup or self.get_schema_markup(post)
        
        return context
    
    def get_schema_markup(self, post):
        """Generate JSON-LD schema markup for rich snippets"""
        schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post.title,
            "description": post.excerpt,
            "datePublished": post.created_at.isoformat(),
            "dateModified": post.updated_at.isoformat(),
            "author": {
                "@type": "Person",
                "name": post.author
            },
            "publisher": {
                "@type": "Organization",
                "name": "Anwaar Galaxy Glow",
                "logo": {
                    "@type": "ImageObject",
                    "url": self.request.build_absolute_uri('/static/images/logo.png')
                }
            }
        }
        
        if post.featured_image:
            schema["image"] = {
                "@type": "ImageObject",
                "url": self.request.build_absolute_uri(post.featured_image.url),
                "caption": post.featured_image_alt or post.title
            }
        
        if post.category:
            schema["articleSection"] = post.category.name
        
        if post.tags:
            schema["keywords"] = post.get_tags_display()
        
        if post.reading_time:
            schema["timeRequired"] = f"PT{post.reading_time}M"
        
        return schema

class BlogCategoryView(ListView):
    model = BlogPost
    template_name = 'blog/blog_category.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        self.category = get_object_or_404(BlogCategory, slug=self.kwargs['category_slug'])
        return BlogPost.objects.filter(
            is_published=True,
            category=self.category
        ).select_related('category').order_by('-is_featured', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all categories for sidebar
        context['all_categories'] = BlogCategory.objects.annotate(
            post_count=Count('posts', filter=Q(posts__is_published=True))
        ).filter(post_count__gt=0)
        
        # SEO Meta
        context['meta_title'] = self.category.meta_title or f"{self.category.name} - Blog"
        context['meta_description'] = self.category.meta_description or f"Browse all articles in the {self.category.name} category."
        context['meta_keywords'] = self.category.meta_keywords
        context['canonical_url'] = self.request.build_absolute_uri()
        
        return context

class BlogSearchView(ListView):
    model = BlogPost
    template_name = 'blog/blog_search.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return BlogPost.objects.filter(
                is_published=True
            ).filter(
                Q(title__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__icontains=query) |
                Q(category__name__icontains=query)
            ).select_related('category').order_by('-created_at')
        return BlogPost.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        
        # SEO Meta
        context['meta_title'] = f"Search Results for '{context['search_query']}' - Blog"
        context['meta_description'] = f"Search results for '{context['search_query']}' on our blog."
        context['canonical_url'] = self.request.build_absolute_uri()
        
        return context