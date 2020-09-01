from django import forms
from .models import Documents, Sentiments

class tag_selection_form(forms.Form):
    tag1 = forms.CharField(label='Tag 1', max_length=20)
    tag2 = forms.CharField(label='Tag 2', max_length=20)
    tag3 = forms.CharField(label='Tag 3', max_length=20)
    tag4 = forms.CharField(label='Tag 4', max_length=20)
    tag5 = forms.CharField(label='Tag 5', max_length=20)

class model_name_selection_form(forms.Form):
	name = forms.CharField(label='Model Name', max_length=20)
	
class upload_file_form(forms.ModelForm):
    class Meta:
        model = Documents
        fields = ('description', 'document')

class sentiments_form(forms.ModelForm):
    text  = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Sentiments
        fields = ('title', 'text', 'author')