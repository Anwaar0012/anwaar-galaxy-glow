# testimonials/templatetags/testimonials_tags.py
from django import template
from ..models import Testimonial

register = template.Library()

@register.inclusion_tag('testimonials/includes/featured_testimonials.html')
def featured_testimonials(limit=3):
    return {
        'testimonials': Testimonial.objects.filter(
            is_active=True, is_featured=True
        ).only('client_name', 'testimonial', 'rating', 'client_image', 'company')[:limit]
    }