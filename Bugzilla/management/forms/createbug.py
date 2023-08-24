from django import forms
from ..models import Bug, Project

class CreateBugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ['title', 'description', 'screenshot', 'type', 'status', 'start_date', 'deadline', 'project', 'developer']
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'border border-black py-2 px-4 w-full'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'border border-black py-2 px-4 w-full'}))
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    deadline = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
