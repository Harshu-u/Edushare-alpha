from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views import View
from django.db.models import Q, Avg, Prefetch
from django.http import JsonResponse, HttpResponseForbidden
# This is the import you added, which is correct!
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .models import Note, Rating, Tag 
from categories.models import Category
from .forms import NoteForm, RatingForm

# Mixin to check if user is the owner or a teacher/admin
class OwnerOrTeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_teacher() or self.request.user.is_staff or (obj.uploader == self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to modify this note.")
        return redirect('notes:note-list')

#
# --- THIS IS THE UPDATED CLASS ---
#
class NoteListView(ListView):
    model = Note
    template_name = 'notes/note_list.html'
    context_object_name = 'notes'
    paginate_by = 12

    def get_queryset(self):
        # Start with the base, optimized queryset
        queryset = Note.objects.filter(is_public=True).select_related('uploader', 'category').prefetch_related('tags')
        
        search_query = self.request.GET.get('q', '')
        category_query = self.request.GET.get('category', '')
        sort_query = self.request.GET.get('sort', '-created_at')

        if search_query:
            # --- NEW: Full-Text Search ---
            # 1. Define what fields to search against, and with what priority
            vector = SearchVector('title', weight='A') + \
                     SearchVector('tags__name', weight='A') + \
                     SearchVector('description', weight='B') + \
                     SearchVector('category__name', weight='B') + \
                     SearchVector('uploader__first_name', weight='C') + \
                     SearchVector('uploader__last_name', weight='C')
            
            # 2. Create the query
            query = SearchQuery(search_query)
            
            # 3. Filter the queryset by rank, and sort by the most relevant first
            queryset = queryset.annotate(
                rank=SearchRank(vector, query)
            ).filter(rank__gte=0.1).order_by('-rank')
            # --- END NEW SEARCH ---
        
        elif category_query:
            # Only filter by category if not searching
            queryset = queryset.filter(category__pk=category_query)
            
        elif sort_query in ['-average_rating', '-created_at', 'title']:
             # Only apply sort_query if we are NOT searching
             # (since search results should be sorted by rank)
             queryset = queryset.order_by(sort_query)
             
        if category_query and search_query:
            # OPTIONAL: If you want to filter by category *on top of* search results
            queryset = queryset.filter(category__pk=category_query)

        # .distinct() is still good practice when joining on ManyToMany fields (like tags)
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        # Convert category_query to int for proper comparison in template if it exists
        try:
            context['category_query'] = int(self.request.GET.get('category', ''))
        except (ValueError, TypeError):
            context['category_query'] = ''
        context['sort_query'] = self.request.GET.get('sort', '-created_at')
        return context
#
# --- END OF UPDATED CLASS ---
#


class NoteDetailView(DetailView):
    model = Note
    template_name = 'notes/note_detail.html'
    context_object_name = 'note'
    
    def get_queryset(self):
        return super().get_queryset().select_related('uploader', 'category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = self.get_object()
        
        if not note.is_public and self.request.user != note.uploader and not self.request.user.is_staff:
             pass

        if self.request.user.is_authenticated:
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
        form.instance.uploader = self.request.user
        
        # --- NEW: "VILLAIN ARC" REPUTATION LOGIC ---
        # Get the uploader object
        uploader = self.request.user
        # Grant reputation for uploading a new note
        uploader.reputation += 10 
        uploader.save()
        # --- END NEW ---
        
        messages.success(self.request, "Note has been uploaded successfully! (+10 REP)")
        return super().form_valid(form)

class NoteUpdateView(OwnerOrTeacherRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    
    def get_queryset(self):
        return super().get_queryset().prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f"Edit Note: {self.object.title}"
        return context
    
    def get_success_url(self):
        return reverse('notes:note-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Note has been updated successfully!")
        return super().form_valid(form)

class NoteDeleteView(OwnerOrTeacherRequiredMixin, DeleteView):
    model = Note
    template_name = 'notes/note_confirm_delete.html'
    success_url = reverse_lazy('notes:note-list')
    
    def form_valid(self, form):
        # --- NEW: "VILLAIN ARC" REPUTATION LOGIC ---
        # Penalize for deleting a note
        uploader = self.object.uploader
        uploader.reputation -= 10 # -10 rep for deleting
        uploader.save()
        # --- END NEW ---
        
        messages.success(self.request, f'Note "{self.object.title}" has been deleted. (-10 REP)')
        return super().form_valid(form)

class RateNoteView(LoginRequiredMixin, View):
    """
    Handles POST requests to rate a note.
    This view is designed to be called via AJAX (Fetch API).
    """
    def post(self, request, pk):
        try:
            note = get_object_or_404(Note.objects.select_related('uploader'), pk=pk)
            rating_value = int(request.POST.get('rating'))
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid rating value.'}, status=400)
        
        if not (1 <= rating_value <= 5):
            return JsonResponse({'success': False, 'error': 'Rating must be between 1 and 5.'}, status=400)
            
        if note.uploader == request.user:
            return JsonResponse({'success': False, 'error': 'You cannot rate your own note.'}, status=403)

        # Find existing rating
        existing_rating = Rating.objects.filter(note=note, user=request.user).first()
        
        # --- NEW: "VILLAIN ARC" REPUTATION LOGIC ---
        uploader = note.uploader
        rep_message = ""

        if existing_rating:
            # User is CHANGING their rating
            old_value = existing_rating.value
            
            # Revert old reputation change
            if old_value >= 4:
                uploader.reputation -= 5
            elif old_value <= 2:
                uploader.reputation += 2
                
            # Apply new reputation change
            if rating_value >= 4:
                uploader.reputation += 5
                rep_message = "(+5 REP for uploader)"
            elif rating_value <= 2:
                uploader.reputation -= 2
                rep_message = "(-2 REP for uploader)"
        
        else:
            # User is CREATING a new rating
            if rating_value >= 4:
                uploader.reputation += 5
                rep_message = "(+5 REP for uploader)"
            elif rating_value <= 2:
                uploader.reputation -= 2
                rep_message = "(-2 REP for uploader)"
        
        uploader.save()
        # --- END NEW ---

        # Find existing rating or create a new one
        rating, created = Rating.objects.update_or_create(
            note=note,
            user=request.user,
            defaults={'value': rating_value}
        )
        
        # --- NEW: EXPLICITLY UPDATE NOTE RATING ---
        # This fixes the bug from the seeder
        note.update_rating()
        # --- END NEW ---

        return JsonResponse({
            'success': True,
            'average_rating': round(note.average_rating, 1),
            'total_ratings': note.total_ratings,
            'user_rating': rating.value,
            'message': f'Rating submitted! {rep_message}'
        })

class MyNotesView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'notes/note_list.html' 
    context_object_name = 'notes'
    paginate_by = 12

    def get_queryset(self):
        queryset = Note.objects.filter(uploader=self.request.user).select_related('uploader', 'category').prefetch_related('tags')
        
        sort_query = self.request.GET.get('sort', '-created_at')
        if sort_query in ['-average_rating', '-created_at', 'title']:
             queryset = queryset.order_by(sort_query)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "My Notes"
        context['is_my_notes_page'] = True 
        context['sort_query'] = self.request.GET.get('sort', '-created_at')
        return context

class NoteSearchView(NoteListView):
    template_name = 'notes/note_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context['page_title'] = f"Search Results for \"{query}\""
        return context