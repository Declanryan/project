from django import forms
from .models import Topic_extraction_Documents

	
class upload_file_form(forms.ModelForm):
    class Meta:
        model = Topic_extraction_Documents
        fields = ('description', 'document')


class topic_extraction_form(forms.Form):
    CHOICES =( 
    ("1", "5"), 
    ("2", "10"), 
    ("3", "15"), 
    ("4", "20"),
    ("5", "25"), 
    ("6", "30"), 
    ("7", "35"), 
    ("8", "40"),
    ("9", "45"),
    ("10", "50")) 
    
    No_of_topics = forms.MultipleChoiceField(choices=CHOICES)