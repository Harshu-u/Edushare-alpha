from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import User
from django.contrib.auth.forms import UserCreationForm

class HomeView(TemplateView):
    template_name = 'core/home.html'

class RegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'core/register.html'
    success_url = reverse_lazy('login')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'core/profile.html'

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'core/profile_update.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user
