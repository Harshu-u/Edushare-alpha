from django import forms
from .models import Note, Rating
from categories.models import Category

class NoteForm(forms.ModelForm):
    
    # --- NEW: "VILLAIN ARC" STYLES ---
    FORM_INPUT_CLASSES = 'form-input w-full px-4 py-2 rounded-lg bg-background/70 border border-border/50 text-sm shadow-sm placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary'
    FORM_SELECT_CLASSES = 'form-select w-full px-4 py-2 rounded-lg bg-background/70 border border-border/50 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary'
    FORM_TEXTAREA_CLASSES = 'form-input w-full px-4 py-2 rounded-lg bg-background/70 border border-border/50 text-sm shadow-sm placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary'
    
    # This class is now used for the custom drag-and-drop JS, but we define it here for consistency
    FORM_FILE_CLASSES = 'form-file-input' 
    
    FORM_CHECKBOX_CLASSES = 'h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary'
    # --- END NEW STYLES ---

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
                 # We will hide this and use a custom JS interface
                 field.widget.attrs.update({'class': self.FORM_FILE_CLASSES, 'x-ref': 'fileInput'})
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
            'file': forms.FileInput(), # Ensure this is FileInput
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