from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
def upload_to(instance, filename):
		return 'documents/summary/{0}/{1}'.format(instance.author.id , filename)

class Summary_Documents(models.Model):
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


class Summary(models.Model):
	title = models.CharField(max_length=20)
	summary=models.TextField(default='test')
	text = models.CharField(max_length=5000)
	request_sent = models.DateTimeField(auto_now_add=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
	    return self.title
