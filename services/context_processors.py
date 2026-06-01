# services/context_processors.py
from .models import ServiceCategory
from services.models import ServiceCategory, Service

def services_context(request):
    categories = ServiceCategory.objects.all().order_by('order')
    return {
        'service_categories': categories
    }
    
# def footer_services(request):
#     """Add services grouped by category for footer navigation"""
#     categories = ServiceCategory.objects.prefetch_related('services').filter(
#         services__isnull=False
#     ).distinct().order_by('order')
    
#     # Group services by category (limit to first 5 services per category)
#     services_by_category = {}
#     for category in categories:
#         services_by_category[category] = category.services.all().order_by('order')[:5]
    
#     return {
#         'footer_categories': services_by_category
#     }