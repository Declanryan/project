from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


# Create your models here.
class Classification_Documents(models.Model):
	username = models.CharField(default=User, max_length=255)
	description = models.CharField(max_length=255, blank=True)
	document = models.FileField(upload_to='documents/')
	uploaded_at = models.DateTimeField(auto_now_add=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.description

	def delete(self, *args, **kwargs):
		self.document.delete()
		super().delete(*args, **kwargs)



 