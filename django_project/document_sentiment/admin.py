from django.contrib import admin
from .models import Sentiment_Documents, Sentiments

# Register your models here.
admin.site.register(Sentiment_Documents)
admin.site.register(Sentiments)
