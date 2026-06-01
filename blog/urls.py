# blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog_list'),
    path('search/', views.BlogSearchView.as_view(), name='blog_search'),
    path('category/<slug:category_slug>/', views.BlogCategoryView.as_view(), name='blog_category'),
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
]