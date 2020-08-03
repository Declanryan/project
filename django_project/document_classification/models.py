from django.db import models


# Create your models here.
class Documents(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
    	return self.description

    def delete(self, *args, **kwargs):
    	self.document.delete()
    	super().delete(*args, **kwargs)