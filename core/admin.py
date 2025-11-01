from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User # Import your custom User model

# Optional: Customize how the User model appears in the admin
class CustomUserAdmin(UserAdmin):
    model = User
    # --- NEW: Add 'reputation' to the list display ---
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'is_staff', 
        'role', 
        'is_active',
        'reputation' # <-- ADDED
    )
    
    # --- NEW: Add 'reputation' to the main fieldsets ---
    fieldsets = UserAdmin.fieldsets + (
        ('Account Type', {'fields': ('role', 'profile_image', 'bio', 'reputation')}), # <-- ADDED 'reputation'
    )
    
    # Add 'role' to the add user form
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Account Type', {'fields': ('first_name', 'last_name', 'email', 'role')}),
    )
    
    # Make 'role' and 'is_active' filterable
    list_filter = UserAdmin.list_filter + ('role', 'is_active',)
    
    # --- NEW: Make reputation editable ---
    list_editable = ('role', 'is_active', 'reputation',)

# Register your custom User model with the custom admin class
admin.site.register(User, CustomUserAdmin)