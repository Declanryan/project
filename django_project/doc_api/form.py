from django import forms
from . models import sentiment

class sentiment_form(forms.Form):
   class Meta:
        model = sentiment
        fields = ('description', 'text')
