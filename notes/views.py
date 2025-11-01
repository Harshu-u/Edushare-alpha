from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from django.db.models import Q
from .models import Note, Rating

class NoteListView(ListView):
    model = Note
    template_name = 'notes/note_list.html'
    context_object_name = 'notes'
    paginate_by = 12

    def get_queryset(self):
        queryset = Note.objects.filter(is_public=True)
        sort_by = self.request.GET.get('sort')
        if sort_by == 'rating':
            queryset = queryset.order_by('-average_rating')
        return queryset

class NoteDetailView(DetailView):
    model = Note
    template_name = 'notes/note_detail.html'
    context_object_name = 'note'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_rating'] = Rating.objects.filter(
                note=self.object,
                user=self.request.user
            ).first()
        return context

class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    template_name = 'notes/note_form.html'
    fields = ['title', 'description', 'file', 'category', 'is_public']
    success_url = reverse_lazy('note-list')

    def form_valid(self, form):
        form.instance.uploader = self.request.user
        return super().form_valid(form)

class NoteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Note
    template_name = 'notes/note_form.html'
    fields = ['title', 'description', 'file', 'category', 'is_public']

    def test_func(self):
        note = self.get_object()
        return self.request.user == note.uploader or self.request.user.is_teacher()

    def get_success_url(self):
        return reverse_lazy('note-detail', kwargs={'pk': self.object.pk})

class NoteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Note
    template_name = 'notes/note_confirm_delete.html'
    success_url = reverse_lazy('note-list')

    def test_func(self):
        note = self.get_object()
        return self.request.user == note.uploader or self.request.user.is_teacher()

class RateNoteView(LoginRequiredMixin, View):
    """Accepts rating POSTs. Returns JSON when requested via AJAX, otherwise redirects.

    Endpoint: POST /notes/<pk>/rate/
    POST params: rating=int 1-5
    """
    def post(self, request, pk):
        note = get_object_or_404(Note, pk=pk)
        try:
            rating_value = int(request.POST.get('rating'))
        except (TypeError, ValueError):
            rating_value = None

        if rating_value and 1 <= rating_value <= 5:
            rating, created = Rating.objects.get_or_create(
                note=note,
                user=request.user,
                defaults={'value': rating_value}
            )

            if not created:
                rating.value = rating_value
                rating.save()

            # Update note's average rating
            ratings = Rating.objects.filter(note=note)
            note.average_rating = sum(r.value for r in ratings) / ratings.count()
            note.total_ratings = ratings.count()
            note.save()

            # If AJAX (X-Requested-With) return JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': True,
                    'average_rating': float(note.average_rating),
                    'total_ratings': note.total_ratings,
                })

            messages.success(request, 'Rating submitted successfully!')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'error': 'Invalid rating value'}, status=400)
            messages.error(request, 'Invalid rating value!')

        return redirect('note-detail', pk=pk)

class MyNotesView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'notes/my_notes.html'
    context_object_name = 'notes'
    paginate_by = 12

    def get_queryset(self):
        return Note.objects.filter(uploader=self.request.user)

class NoteSearchView(ListView):
    model = Note
    template_name = 'notes/note_search.html'
    context_object_name = 'notes'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Note.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query) |
                Q(uploader__username__icontains=query)
            ).filter(is_public=True).order_by('-created_at')
        return Note.objects.none()
