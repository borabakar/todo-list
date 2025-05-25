from django import forms
from .models import Task
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'assigned_to', 'priority']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }