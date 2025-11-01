from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    
    # Define common CSS classes from campusconnect
    FORM_INPUT_CLASSES = 'form-input w-full px-4 py-2 rounded-lg border border-input bg-background text-sm shadow-sm placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary'
    FORM_SELECT_CLASSES = 'form-select w-full px-4 py-2 rounded-lg border border-input bg-background text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary'
    FORM_TEXTAREA_CLASSES = 'form-input w-full px-4 py-2 rounded-lg border border-input bg-background text-sm shadow-sm placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply Tailwind classes to all fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                 field.widget.attrs.update({'class': self.FORM_TEXTAREA_CLASSES, 'rows': 3})
            elif isinstance(field.widget, forms.Select):
                 field.widget.attrs.update({'class': self.FORM_SELECT_CLASSES})
            else:
                 field.widget.attrs.update({'class': self.FORM_INPUT_CLASSES})
        
        # Make the 'parent' field not required
        self.fields['parent'].required = False

    class Meta:
        model = Category
        fields = ['name', 'parent', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }