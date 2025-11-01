from django.contrib import admin
from .models import Note, Rating

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
    search_fields = ('title', 'description', 'uploader__username')
    list_editable = ('is_public',)
    autocomplete_fields = ('uploader', 'category') # Makes linking easier in admin

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('note', 'user', 'value', 'created_at')
    list_filter = ('value', 'created_at')
    search_fields = ('note__title', 'user__username')
    autocomplete_fields = ('note', 'user')