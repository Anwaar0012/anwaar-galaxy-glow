# projects/urls.py
from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Main portfolio
    path('', views.ProjectListView.as_view(), name='project_list'),
    
    # Category filtering
    path('category/<slug:category_slug>/', views.ProjectCategoryView.as_view(), name='project_category'),
    
    # Technology filtering (optional)
    path('technology/<str:technology>/', views.ProjectListView.as_view(), name='project_technology'),
    
    # Individual project
    path('<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
]