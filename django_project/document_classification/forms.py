from django import forms
from .models import Classification_Documents

class tag_selection_form(forms.Form):
    tag0 = forms.CharField(label='Tag0', max_length=20)
    tag1 = forms.CharField(label='Tag1', max_length=20)
    tag2 = forms.CharField(label='Tag2', max_length=20)
    tag3 = forms.CharField(label='Tag3', max_length=20)
    tag4 = forms.CharField(label='Tag4', max_length=20)
    tag5 = forms.CharField(label='Tag5', max_length=20)
    tag6 = forms.CharField(label='Tag6', max_length=20)
    tag7 = forms.CharField(label='Tag7', max_length=20)
    tag8 = forms.CharField(label='Tag8', max_length=20)
    tag9 = forms.CharField(label='Tag9', max_length=20)

class model_name_selection_form(forms.Form):
	name = forms.CharField(label='Model Name', max_length=20)
	
class upload_file_form(forms.ModelForm):
    class Meta:
        model = Classification_Documents
        fields = ('description', 'document')