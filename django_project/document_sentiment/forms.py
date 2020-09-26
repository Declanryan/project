from django import forms
from .models import Sentiment_Documents, Sentiments
	
class upload_file_form(forms.ModelForm):
    class Meta:
        model = Sentiment_Documents
        fields = ('description', 'document')

class sentiments_form(forms.ModelForm):
    text  = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Sentiments
        fields = ('title', 'text', 'author')