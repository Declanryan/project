from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



def upload_to(instance, filename):
		return 'documents/topic/{0}/{1}'.format(instance.author.id , filename)


class Topic_extraction_Documents(models.Model):
	username = models.CharField(default=User, max_length=255)
	description = models.CharField(max_length=255, blank=True)
	document = models.FileField(upload_to=upload_to)
	uploaded_at = models.DateTimeField(auto_now_add=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.description

	def delete(self, *args, **kwargs):
		self.document.delete()
		super().delete(*args, **kwargs)