from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Documents(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    #username = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
    	return self.description

    def delete(self, *args, **kwargs):
    	self.document.delete()
    	super().delete(*args, **kwargs)

    def extract(self, *args, **kwargs):
    	self.


class Sentiments(models.Model):
	title = models.CharField(max_length=20)
	text = models.CharField(max_length=500)
	request_sent = models.DateTimeField(auto_now_add=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
	    return self.title

 