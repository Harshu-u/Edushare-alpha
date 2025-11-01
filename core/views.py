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
    # We will create this template in the next batch
    return render(request, 'core/landing.html')

# View for the dashboard (requires login)
@login_required
def dashboard_view(request):
    
    # --- 1. Top Stat Cards (EduShare Stats) ---
    note_count = Note.objects.count()
    category_count = Category.objects.count()
    user_count = User.objects.filter(is_active=True).count()
    
    # Calculate overall average rating
    overall_avg_rating = Note.objects.aggregate(avg=Avg('average_rating'))['avg'] or 0.0
    
    # --- 2. Chart Data: Notes per Category ---
    category_notes = Category.objects.annotate(count=Count('notes')).order_by('-count')
    cat_labels = json.dumps([c.name for c in category_notes])
    cat_data = json.dumps([c.count for c in category_notes])

    # --- 3. Recent/Top Notes ---
    recent_notes = Note.objects.select_related('uploader', 'category').filter(is_public=True).order_by('-created_at')[:5]
    top_notes = Note.objects.select_related('uploader', 'category').filter(is_public=True).order_by('-average_rating')[:5]

    # --- 4. Alerts & Quick Info (EduShare specific) ---
    pending_teachers = User.objects.filter(role='teacher', is_active=False).count()
    unrated_notes = Note.objects.filter(total_ratings=0).count()


    context = {
        'note_count': note_count,
        'category_count': category_count,
        'user_count': user_count,
        'overall_avg_rating': round(overall_avg_rating, 1),
        
        'category_chart_labels': cat_labels,
        'category_chart_data': cat_data,
        
        'recent_notes': recent_notes,
        'top_notes': top_notes,
        
        'pending_teachers_count': pending_teachers,
        'unrated_notes_count': unrated_notes,
    } 
    # We will create this template in the next batch
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
    
    # We will create this template in the next batch
    return render(request, 'registration/register.html', {'form': form})