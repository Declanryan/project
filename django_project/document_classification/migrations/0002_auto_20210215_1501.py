# Generated by Django 3.0.3 on 2021-02-15 15:01

from django.db import migrations, models
import document_classification.models


class Migration(migrations.Migration):

    dependencies = [
        ('document_classification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classification_documents',
            name='document',
            field=models.FileField(upload_to=document_classification.models.upload_to),
        ),
    ]
