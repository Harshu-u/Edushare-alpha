from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from datetime import date, timedelta

# Import models for Dashboard
from notes.models import Note
from categories.models import Category
from core.models import User
from django.db.models import Count, Avg

# View for the public landing page
def landing_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    # This template was updated in the "Villain Arc"
    return render(request, 'core/landing.html')

# View for the dashboard (requires login)
@login_required
def dashboard_view(request):
    
    # --- "VILLAIN ARC" DATA QUERIES ---
    
    # 1. Top Stat Cards (Same as before)
    note_count = Note.objects.count()
    category_count = Category.objects.count()
    user_count = User.objects.filter(is_active=True).count()
    
    # 2. Chart Data: Notes per Category (Same as before)
    category_notes = Category.objects.annotate(count=Count('notes')).order_by('-count')
    cat_labels = json.dumps([c.name for c in category_notes])
    cat_data = json.dumps([c.count for c in category_notes])

    # 3. Recent/Top Notes (Same as before)
    recent_notes = Note.objects.select_related('uploader', 'category').filter(is_public=True).order_by('-created_at')[:5]
    top_notes = Note.objects.select_related('uploader', 'category').filter(is_public=True).order_by('-average_rating')[:5]

    # 4. --- NEW: LEADERBOARD DATA ---
    # Get the top 5 users, ordered by their reputation
    top_users = User.objects.filter(is_active=True).order_by('-reputation')[:5]
    # --- END NEW DATA ---

    context = {
        'note_count': note_count,
        'category_count': category_count,
        'user_count': user_count,
        
        'category_chart_labels': cat_labels,
        'category_chart_data': cat_data,
        
        'recent_notes': recent_notes,
        'top_notes': top_notes,
        
        'top_users': top_users, # <-- The missing piece!
    } 
    # This template was updated in the "Villain Arc"
    return render(request, 'core/dashboard.html', context)

# View for registration (with APPROVAL LOGIC)
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # Don't save to DB yet
            
            # --- APPROVAL LOGIC ---
            if user.role == 'student':
                user.is_active = True  # Students are approved automatically
            elif user.role == 'teacher':
                user.is_active = False # Faculty MUST be approved by admin
            # --- END NEW LOGIC ---
            
            user.save() # Now save the user
            
            # Only log in if they are active (i.e., students)
            if user.is_active:
                login(request, user)
                messages.success(request, 'Your account has been created successfully!')
                return redirect('dashboard')
            else:
                # Send faculty to the login page with a message
                messages.info(request, 'Your Teacher account has been created. It must be approved by an administrator before you can log in.')
                return redirect('login') 
    else:
        form = CustomUserCreationForm()
    
    # This template was updated in the "Villain Arc"
    return render(request, 'registration/register.html', {'form': form})