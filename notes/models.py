from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from categories.models import Category # Import the Category model
from django.urls import reverse
from django.db.models import Avg
from django.utils.text import slugify # --- NEW: Import slugify

# ---
# NEW: "VILLAIN ARC" TAG MODEL
# ---
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate slug from name if it's blank
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# ---
# NOTE MODEL (Updated)
# ---
class Note(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='notes/', help_text="Upload your note (PDF, DOCX, PPT)")
    
    # Relationships
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="notes"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="notes"
    )
    # --- NEW: TAGS FIELD ---
    tags = models.ManyToManyField(
        Tag, 
        blank=True, 
        related_name="notes"
    )
    # --- END NEW FIELD ---
    
    # Status & Rating
    is_public = models.BooleanField(default=True, help_text="Allow anyone (even guests) to see this note.")
    average_rating = models.FloatField(default=0.0)
    total_ratings = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('notes:note-detail', kwargs={'pk': self.pk})

    def update_rating(self):
        """
        Recalculates the average rating and total ratings for a note.
        This is called by the Rating model when a rating is saved or deleted.
        """
        ratings_data = self.ratings.aggregate(
            average=Avg('value'),
            count=models.Count('id')
        )
        
        self.average_rating = ratings_data['average'] or 0.0
        self.total_ratings = ratings_data['count'] or 0
        self.save()

# ---
# RATING MODEL (Unchanged)
# ---
class Rating(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can only rate a specific note once
        unique_together = ('note', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} rated {self.note.title} with {self.value} stars"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # After saving, trigger the note to update its average rating
        self.note.update_rating()

    def delete(self, *args, **kwargs):
        note = self.note
        super().delete(*args, **kwargs)
        # After deleting, trigger the note to update its average rating
        note.update_rating()