from django import forms

class tag_selection_form(forms.Form):
    tag1 = forms.CharField(label='Tag 1', max_length=20)
    tag2 = forms.CharField(label='Tag 2', max_length=20)
    tag3 = forms.CharField(label='Tag 3', max_length=20)
    tag4 = forms.CharField(label='Tag 4', max_length=20)
    tag5 = forms.CharField(label='Tag 5', max_length=20)

class model_name_selection_form(forms.Form):
	name = forms.CharField(label='Model Name', max_length=20)
	