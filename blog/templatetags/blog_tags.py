# blog/templatetags/blog_tags.py
from django import template
from ..models import BlogPost, BlogCategory

register = template.Library()

@register.inclusion_tag('blog/tags/recent_posts.html')
def recent_posts(count=5):
    return {'recent_posts': BlogPost.objects.filter(is_published=True)[:count]}

@register.inclusion_tag('blog/tags/popular_posts.html')
def popular_posts(count=5):
    return {'popular_posts': BlogPost.objects.filter(is_published=True).order_by('-views')[:count]}

@register.inclusion_tag('blog/tags/categories_list.html')
def categories_list():
    return {'categories': BlogCategory.objects.all()}

@register.simple_tag
def get_reading_time(content):
    word_count = len(content.split())
    return max(1, round(word_count / 200))