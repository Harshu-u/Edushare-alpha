from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views import View
from django.db.models import Q, Avg
from django.http import JsonResponse, HttpResponseForbidden

from .models import Note, Rating
from categories.models import Category
from .forms import NoteForm, RatingForm

# Mixin to check if user is the owner or a teacher/admin
class OwnerOrTeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        # Allow if user is a teacher/admin OR if they are the uploader
        return self.request.user.is_teacher() or self.request.user.is_staff or (obj.uploader == self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to modify this note.")
        return redirect('notes:note-list')

class NoteListView(ListView):
    model = Note
    template_name = 'notes/note_list.html'
    context_object_name = 'notes'
    paginate_by = 12

    def get_queryset(self):
        # Start with all public notes
        queryset = Note.objects.filter(is_public=True).select_related('uploader', 'category')
        
        # Get filter queries from URL
        search_query = self.request.GET.get('q', '')
        category_query = self.request.GET.get('category', '')
        sort_query = self.request.GET.get('sort', '-created_at')

        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(uploader__first_name__icontains=search_query) |
                Q(uploader__last_name__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Apply category filter
        if category_query:
            queryset = queryset.filter(category__pk=category_query)
            
        # Apply sorting
        if sort_query in ['-average_rating', '-created_at', 'title']:
             queryset = queryset.order_by(sort_query)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        context['category_query'] = self.request.GET.get('category', '')
        context['sort_query'] = self.request.GET.get('sort', '-created_at')
        return context


class NoteDetailView(DetailView):
    model = Note
    template_name = 'notes/note_detail.html'
    context_object_name = 'note'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = self.get_object()
        
        # Check if guest or non-public
        if not note.is_public and self.request.user != note.uploader and not self.request.user.is_staff:
             # This will be caught by the template or we can raise 404
             pass

        if self.request.user.is_authenticated:
            # Get the current user's rating for this note, if it exists
            user_rating = Rating.objects.filter(note=note, user=self.request.user).first()
            context['user_rating_value'] = user_rating.value if user_rating else 0
        
        context['rating_form'] = RatingForm()
        return context

class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    success_url = reverse_lazy('notes:note-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Upload a New Note"
        return context

    def form_valid(self, form):
        # Assign the logged-in user as the uploader
        form.instance.uploader = self.request.user
        messages.success(self.request, "Note has been uploaded successfully!")
        return super().form_valid(form)

class NoteUpdateView(OwnerOrTeacherRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f"Edit Note: {self.object.title}"
        return context
    
    def get_success_url(self):
        # Redirect back to the detail page of the note we just edited
        return reverse('notes:note-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Note has been updated successfully!")
        return super().form_valid(form)

class NoteDeleteView(OwnerOrTeacherRequiredMixin, DeleteView):
    model = Note
    template_name = 'notes/note_confirm_delete.html'
    success_url = reverse_lazy('notes:note-list')

    def form_valid(self, form):
        messages.success(self.request, f'Note "{self.object.title}" has been deleted.')
        return super().form_valid(form)

class RateNoteView(LoginRequiredMixin, View):
    """
    Handles POST requests to rate a note.
    This view is designed to be called via AJAX (Fetch API).
    """
    def post(self, request, pk):
        try:
            note = get_object_or_404(Note, pk=pk)
            rating_value = int(request.POST.get('rating'))
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid rating value.'}, status=400)
        
        if not (1 <= rating_value <= 5):
            return JsonResponse({'success': False, 'error': 'Rating must be between 1 and 5.'}, status=400)

        # Find existing rating or create a new one
        rating, created = Rating.objects.update_or_create(
            note=note,
            user=request.user,
            defaults={'value': rating_value}
        )

        return JsonResponse({
            'success': True,
            'average_rating': round(note.average_rating, 1),
            'total_ratings': note.total_ratings,
            'user_rating': rating.value,
            'message': 'Rating submitted successfully!'
        })

class MyNotesView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'notes/note_list.html' # Re-use the main list template
    context_object_name = 'notes'
    paginate_by = 12

    def get_queryset(self):
        # Filter notes by the currently logged-in user
        queryset = Note.objects.filter(uploader=self.request.user).select_related('uploader', 'category')
        
        # Add sorting (same as NoteListView)
        sort_query = self.request.GET.get('sort', '-created_at')
        if sort_query in ['-average_rating', '-created_at', 'title']:
             queryset = queryset.order_by(sort_query)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Override the page title
        context['page_title'] = "My Notes"
        context['is_my_notes_page'] = True # Flag to change titles in template
        context['sort_query'] = self.request.GET.get('sort', '-created_at')
        return context

class NoteSearchView(NoteListView):
    """
    This view is just an alias for the NoteListView.
    The list view itself handles the search logic based on GET parameters.
    We just change the template to be more specific if we want.
    """
    template_name = 'notes/note_list.html' # Can reuse the same template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context['page_title'] = f"Search Results for \"{query}\""
        return context