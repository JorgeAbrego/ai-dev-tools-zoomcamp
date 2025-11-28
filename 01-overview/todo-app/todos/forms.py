from django import forms
from .models import Todo


class TodoForm(forms.ModelForm):
    """Form for creating and editing TODO items."""
    
    class Meta:
        model = Todo
        fields = ['title', 'description', 'due_date', 'is_resolved']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter TODO title...',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Enter description...',
                'rows': 4,
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'is_resolved': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }
