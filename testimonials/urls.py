# testimonials/urls.py
from django.urls import path
from . import views

app_name = 'testimonials'

urlpatterns = [
    # Main testimonial listing page
    path('', views.TestimonialListView.as_view(), name='testimonial_list'),
    
    # Submit a new testimonial (this was missing!)
    path('submit/', views.TestimonialSubmitView.as_view(), name='submit'),
    
    # Thank you page after submission (this was missing!)
    path('thank-you/', views.TestimonialThankYouView.as_view(), name='thank_you'),
    
    # Individual testimonial detail view (optional but good)
    path('<int:pk>/', views.TestimonialDetailView.as_view(), name='detail'),
    
    # Admin view for pending testimonials (optional)
    path('pending/', views.TestimonialAdminPendingListView.as_view(), name='admin_pending'),
]
