# Generated by Django 3.0.3 on 2021-03-15 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_summary', '0004_auto_20210315_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summary',
            name='text',
            field=models.CharField(max_length=5000),
        ),
    ]