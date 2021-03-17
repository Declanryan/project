from django import forms
from .models import Extraction_Documents


class upload_file_form(forms.ModelForm):
    class Meta:
        model = Extraction_Documents
        fields = ('description', 'document')

