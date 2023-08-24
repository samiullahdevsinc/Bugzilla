from django import forms
from ..models import Project

class EditProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name","developer","qa"] # Add more fields if needed
