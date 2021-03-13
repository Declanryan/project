from django import forms
from .models import Summary_Documents, Summary
	
class upload_file_form(forms.ModelForm):
    class Meta:
        model = Summary_Documents
        fields = ('description', 'document')

class summary_form(forms.ModelForm):
    text  = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Summary
        fields = ('title', 'text')