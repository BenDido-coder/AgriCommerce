# Generated by Django 5.2.1 on 2025-05-26 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ac', '0017_alter_product_is_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
