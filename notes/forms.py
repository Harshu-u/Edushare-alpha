from django import forms
from .models import Note, Rating, Tag 
import json 

class NoteForm(forms.ModelForm):
    
    # --- "VILLAIN ARC" STYLES ---
    FORM_INPUT_CLASSES = 'form-input w-full px-4 py-2 rounded-lg bg-background/70 border border-border/50 text-sm shadow-sm placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary'
    FORM_SELECT_CLASSES = 'form-select w-full px-4 py-2 rounded-lg bg-background/70 border border-border/50 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary'
    FORM_TEXTAREA_CLASSES = 'form-input w-full px-4 py-2 rounded-lg bg-background/70 border border-border/50 text-sm shadow-sm placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary'
    FORM_FILE_CLASSES = 'form-file-input' 
    FORM_CHECKBOX_CLASSES = 'h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary'
    
    # --- TAGS FIELD ---
    tags = forms.CharField(
        required=False,
        help_text="Enter tags (e.g., python, dsa, sem4)",
        widget=forms.TextInput(attrs={
            'id': 'id_tags_input', # We need a consistent ID for the JS to find
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['tags'].initial = ', '.join([t.name for t in self.instance.tags.all()])

        # Apply Tailwind classes to all fields
        for field_name, field in self.fields.items():
            if field_name == 'tags': 
                continue
            if isinstance(field.widget, forms.Textarea):
                 field.widget.attrs.update({'class': self.FORM_TEXTAREA_CLASSES, 'rows': 4})
            elif isinstance(field.widget, forms.Select):
                 field.widget.attrs.update({'class': self.FORM_SELECT_CLASSES})
            elif isinstance(field.widget, forms.CheckboxInput):
                 field.widget.attrs.update({'class': self.FORM_CHECKBOX_CLASSES})
            elif isinstance(field.widget, forms.FileInput):
                 field.widget.attrs.update({'class': self.FORM_FILE_CLASSES, 'x-ref': 'fileInput'})
            else:
                 field.widget.attrs.update({'class': self.FORM_INPUT_CLASSES})
        
        self.fields['category'].required = False

    class Meta:
        model = Note
        fields = [
            'title', 
            'category', 
            # --- THE BUG FIX: 'tags' is REMOVED from this list ---
            'description', 
            'file', 
            'is_public'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'file': forms.FileInput(), 
        }

    # --- CUSTOM SAVE LOGIC FOR TAGS ---
    def save(self, commit=True):
        # We save with commit=False to get the instance
        # but NOT save the m2m fields yet.
        note = super().save(commit=False)
        
        # Manually save the instance if commit is True
        if commit:
            note.save()

        # Now, we handle the tags ourselves.
        tag_names = []
        try:
            tags_json = self.cleaned_data.get('tags', '[]')
            tag_data = json.loads(tags_json)
            tag_names = [t['value'] for t in tag_data]
        except (json.JSONDecodeError, TypeError):
            tags_str = self.cleaned_data.get('tags', '')
            tag_names = [name.strip() for name in tags_str.split(',') if name.strip()]

        # Find or create new tags and add them to the note
        tags_to_add = []
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name.lower().strip())
            tags_to_add.append(tag)
        
        # This is the correct way to save m2m fields
        note.tags.set(tags_to_add)
        
        return note
    # --- END FIX ---


class RatingForm(forms.ModelForm):
    value = forms.IntegerField(
        min_value=1, 
        max_value=5, 
        widget=forms.HiddenInput() 
    )
    
    class Meta:
        model = Rating
        fields = ['value']