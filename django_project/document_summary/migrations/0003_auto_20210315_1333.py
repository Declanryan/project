# Generated by Django 3.0.3 on 2021-03-15 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_summary', '0002_auto_20210315_0039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summary',
            name='summary',
            field=models.TextField(default='test'),
        ),
    ]
