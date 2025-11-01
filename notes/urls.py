from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    # /notes/ (List all public notes)
    path('', views.NoteListView.as_view(), name='note-list'),
    
    # /notes/create/ (Upload a new note)
    path('create/', views.NoteCreateView.as_view(), name='note-create'),
    
    # /notes/my-notes/ (List notes uploaded by the current user)
    path('my-notes/', views.MyNotesView.as_view(), name='my-notes'),
    
    # /notes/search/ (Search results page)
    path('search/', views.NoteSearchView.as_view(), name='note-search'),
    
    # /notes/5/ (View a single note's details)
    path('<int:pk>/', views.NoteDetailView.as_view(), name='note-detail'),
    
    # /notes/5/edit/ (Edit a note)
    path('<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note-edit'),
    
    # /notes/5/delete/ (Delete a note)
    path('<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note-delete'),
    
    # /notes/5/rate/ (AJAX endpoint for submitting a rating)
    path('<int:pk>/rate/', views.RateNoteView.as_view(), name='note-rate'),
]