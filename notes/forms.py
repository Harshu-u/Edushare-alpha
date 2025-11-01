from django import forms
from .models import Note, Rating
from categories.models import Category

class NoteForm(forms.ModelForm):
    
    # Define common CSS classes from campusconnect
    FORM_INPUT_CLASSES = 'form-input w-full px-4 py-2 rounded-lg border border-input bg-background text-sm shadow-sm placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary'
    FORM_SELECT_CLASSES = 'form-select w-full px-4 py-2 rounded-lg border border-input bg-background text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary'
    FORM_TEXTAREA_CLASSES = 'form-input w-full px-4 py-2 rounded-lg border border-input bg-background text-sm shadow-sm placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary'
    FORM_FILE_CLASSES = 'form-input w-full file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20'
    FORM_CHECKBOX_CLASSES = 'h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply Tailwind classes to all fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                 field.widget.attrs.update({'class': self.FORM_TEXTAREA_CLASSES, 'rows': 4})
            elif isinstance(field.widget, forms.Select):
                 field.widget.attrs.update({'class': self.FORM_SELECT_CLASSES})
            elif isinstance(field.widget, forms.CheckboxInput):
                 field.widget.attrs.update({'class': self.FORM_CHECKBOX_CLASSES})
            elif isinstance(field.widget, forms.FileInput):
                 field.widget.attrs.update({'class': self.FORM_FILE_CLASSES})
            else:
                 field.widget.attrs.update({'class': self.FORM_INPUT_CLASSES})
        
        # Make category optional
        self.fields['category'].required = False

    class Meta:
        model = Note
        fields = [
            'title', 
            'category', 
            'description', 
            'file', 
            'is_public'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class RatingForm(forms.ModelForm):
    """
    A simple form for submitting a rating (1-5).
    """
    value = forms.IntegerField(
        min_value=1, 
        max_value=5, 
        widget=forms.HiddenInput() # The stars will set this value
    )
    
    class Meta:
        model = Rating
        fields = ['value']