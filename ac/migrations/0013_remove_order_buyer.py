# Generated by Django 5.2.1 on 2025-05-25 23:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ac', '0012_load_initial_cities'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='buyer',
        ),
    ]
