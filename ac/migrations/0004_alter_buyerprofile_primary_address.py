# Generated by Django 5.2.1 on 2025-05-17 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ac', '0003_fix_missing_profiles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyerprofile',
            name='primary_address',
            field=models.TextField(blank=True, default='Address not specified'),
        ),
    ]
