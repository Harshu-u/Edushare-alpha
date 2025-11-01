from django.contrib import admin
from .models import Note, Rating, Tag # --- NEW: Import Tag ---

# ---
# NEW: "VILLAIN ARC" TAG ADMIN
# ---
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',) # This is required for the autocomplete to work
    prepopulate_fields = {'slug': ('name',)} # Auto-fills slug from name in admin

# ---
# NOTE ADMIN (Updated)
# ---
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'uploader', 
        'category', 
        'average_rating', 
        'total_ratings', 
        'is_public', 
        'created_at'
    )
    list_filter = ('category', 'is_public', 'created_at')
    # --- NEW: Add tags to search ---
    search_fields = ('title', 'description', 'uploader__username', 'tags__name')
    list_editable = ('is_public',)
    # --- NEW: Add tags to autocomplete ---
    autocomplete_fields = ('uploader', 'category', 'tags')

# ---
# RATING ADMIN (Unchanged)
# ---
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('note', 'user', 'value', 'created_at')
    list_filter = ('value', 'created_at')
    search_fields = ('note__title', 'user__username')
    autocomplete_fields = ('note', 'user')