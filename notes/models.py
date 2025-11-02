from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from categories.models import Category # Import the Category model
from django.urls import reverse
from django.db.models import Avg
from django.utils.text import slugify 

# ---
# TAG MODEL (Unchanged)
# ---
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# ---
# NOTE MODEL (Unchanged)
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
    tags = models.ManyToManyField(
        Tag, 
        blank=True, 
        related_name="notes"
    )
    
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
        This is now called explicitly by RateNoteView or the seeder.
        """
        ratings_data = self.ratings.aggregate(
            average=Avg('value'),
            count=models.Count('id')
        )
        
        self.average_rating = ratings_data['average'] or 0.0
        self.total_ratings = ratings_data['count'] or 0
        self.save()

# ---
# RATING MODEL (MODIFIED)
# ---
class Rating(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('note', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} rated {self.note.title} with {self.value} stars"

    # --- REMOVED `save` and `delete` methods ---
    # We will handle the note update from the view
    # to prevent the bug.