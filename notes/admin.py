from django.contrib import admin
from .models import Note, Rating

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploader', 'category', 'created_at', 'is_public', 'average_rating')
    list_filter = ('category', 'is_public', 'created_at')
    search_fields = ('title', 'description', 'uploader__username')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('note', 'user', 'value', 'created_at')
    list_filter = ('value', 'created_at')
