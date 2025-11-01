from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    # This allows for nested categories (e.g., Science > Physics > Quantum Mechanics)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Categories" # Fixes the "Categorys" typo in admin

    def __str__(self):
        # Show hierarchy in admin dropdowns
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name
    
    def get_absolute_url(self):
        return reverse('categories:category-detail', kwargs={'pk': self.pk})