from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    # Styling classes (kept from CampusConnect theme)
    FORM_INPUT_CLASSES = 'form-input w-full px-4 py-2 rounded-lg border border-input bg-background text-sm shadow-sm placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary'
    FORM_SELECT_CLASSES = 'form-select w-full px-4 py-2 rounded-lg border border-input bg-background text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary'

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, widget=forms.Select(attrs={'class': FORM_SELECT_CLASSES}))

    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': FORM_INPUT_CLASSES, 'placeholder': 'e.g. Aman'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': FORM_INPUT_CLASSES, 'placeholder': 'e.g. Sharma'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': FORM_INPUT_CLASSES, 'placeholder': 'e.g. aman@example.com'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': self.FORM_INPUT_CLASSES, 'placeholder': 'Choose a unique username'})
        self.fields['password2'].widget.attrs.update({'class': self.FORM_INPUT_CLASSES, 'placeholder': 'Confirm your password'})
        self.fields['password1'].widget.attrs.update({'class': self.FORM_INPUT_CLASSES, 'placeholder': 'Enter a strong password'})
