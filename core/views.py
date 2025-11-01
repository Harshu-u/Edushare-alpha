from django.shortcuts import render, redirect
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import User
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.contrib import messages


class HomeView(TemplateView):
    template_name = 'core/home.html'


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Approval logic: students auto-active, teachers require approval
            if getattr(user, 'role', 'student') == 'student':
                user.is_active = True
            else:
                user.is_active = False
            user.save()
            if user.is_active:
                login(request, user)
                messages.success(request, 'Your account has been created successfully!')
                return redirect('home')
            else:
                messages.info(request, 'Your account was created and awaits approval. Please wait for admin activation.')
                return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'core/profile.html'

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'core/profile_update.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user
