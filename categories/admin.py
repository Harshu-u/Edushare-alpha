from django.contrib import admin
from .models import Category
from django.db import models # 👈 *** THIS IS THE FIX ***

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'note_count', 'created_at')
    list_filter = ('parent', 'created_at')
    search_fields = ('name', 'description')
    
    # This improves performance by fetching related data in one query
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _note_count=models.Count('notes', distinct=True)
        )
        return queryset

    def note_count(self, obj):
        return obj._note_count

    note_count.admin_order_field = '_note_count'
    note_count.short_description = 'Notes in Category'