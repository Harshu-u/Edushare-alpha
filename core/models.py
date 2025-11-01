from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        # We can add 'admin' later if we need a non-superuser admin
    )
    
    # 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active'
    # are all inherited from AbstractUser.
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # --- NEW: "VILLAIN ARC" FEATURE ---
    # This will be the foundation for our gamification and leaderboards
    reputation = models.IntegerField(default=0)
    # --- END NEW FEATURE ---
    
    theme_preference = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark'), ('system', 'System')],
        default='system'
    )
    email_notifications = models.BooleanField(default=True)
    account_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # These methods are helpful for permissions
    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def get_age(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None