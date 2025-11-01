from django.urls import path
from . import views

urlpatterns = [
    path('', views.NoteListView.as_view(), name='note-list'),
    path('create/', views.NoteCreateView.as_view(), name='note-create'),
    path('<int:pk>/', views.NoteDetailView.as_view(), name='note-detail'),
    path('<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note-edit'),
    path('<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note-delete'),
    path('<int:pk>/rate/', views.RateNoteView.as_view(), name='note-rate'),
    path('my-notes/', views.MyNotesView.as_view(), name='my-notes'),
    path('search/', views.NoteSearchView.as_view(), name='note-search'),
]