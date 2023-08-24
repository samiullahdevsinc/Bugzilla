from django import forms
from ..models import Bug, Project, userProfile

class EditBugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ['title', 'description', 'screenshot', 'type', 'status', 'start_date', 'deadline', 'project', 'developer']

    # Customize form fields as needed
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'border border-black py-2 px-4 w-full'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'border border-black py-2 px-4 w-full'}))
    screenshot = forms.ImageField(required=False)
    type = forms.ChoiceField(choices=Bug.BUG_TYPES)
    status = forms.ChoiceField(choices=Bug.BUG_STATUS)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    deadline = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    project = forms.ModelChoiceField(queryset=Project.objects.all(), to_field_name='id')  
    developer = forms.ModelChoiceField(queryset=userProfile.objects.filter(user_type='developer'), to_field_name='username') 
