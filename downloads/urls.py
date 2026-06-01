# downloads/urls.py
from django.urls import path
from . import views

app_name = 'downloads'

urlpatterns = [
    path('', views.NoteListView.as_view(), name='note_list'),
    path('category/<slug:category_slug>/', views.NoteListView.as_view(), name='notes_by_category'),
    path('note/<slug:slug>/', views.NoteDetailView.as_view(), name='note_detail'),
    path('note/<slug:slug>/download/', views.download_note, name='download_note'),
    path('drive-folders/', views.GoogleDriveListView.as_view(), name='drive_folders'),
]