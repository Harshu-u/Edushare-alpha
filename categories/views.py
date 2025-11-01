from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Category
from notes.models import Note
from .forms import CategoryForm
from django.db import models

# A mixin to check if the user is a Teacher or Admin
class TeacherOrAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        # Allow if user is a teacher OR a superuser/admin
        return self.request.user.is_teacher() or self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to perform this action.")
        return redirect('categories:category-list')

class CategoryListView(ListView):
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        # Optimize by fetching note count in the same query
        return Category.objects.annotate(note_count=models.Count('notes')).order_by('name')

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'categories/category_detail.html' # We'll create this later
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all public notes in this category
        context['notes'] = Note.objects.filter(
            category=self.object, 
            is_public=True
        ).select_related('uploader')
        return context

class CategoryCreateView(TeacherOrAdminRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('categories:category-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Add New Category"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Category has been added successfully!")
        return super().form_valid(form)

class CategoryUpdateView(TeacherOrAdminRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('categories:category-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f"Edit Category: {self.object.name}"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Category has been updated successfully!")
        return super().form_valid(form)

class CategoryDeleteView(TeacherOrAdminRequiredMixin, DeleteView):
    model = Category
    template_name = 'categories/category_confirm_delete.html' # We'll create this
    success_url = reverse_lazy('categories:category-list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Check if category has notes
        if self.object.notes.exists():
            messages.error(request, f'Cannot delete "{self.object.name}". It is still linked to notes. Please reassign them first.')
            return redirect(self.success_url)
        
        messages.success(request, f'Category "{self.object.name}" has been deleted.')
        return super().post(request, *args, **kwargs)