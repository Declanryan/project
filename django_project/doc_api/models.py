from django.db import models

# Create your models here.

class sentiment(models.Model):
	description= models.CharField(max_length=20)
	text=models.TextField(max_length=500)


	def __str__(self):
		return self.description