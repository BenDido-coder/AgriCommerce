from django.db import migrations

def load_initial_cities(apps, schema_editor):
    City = apps.get_model('ac', 'City')
    cities = [
        ('ADDIS_ABABA', 'Addis Ababa'),
        ('DIRE_DAWA', 'Dire Dawa'),
        ('BAHIR_DAR', 'Bahir Dar'),
        ('MEKELLE', 'Mekelle'),
        ('AWASA', 'Awasa'),
        ('JIMMA', 'Jimma'),
        ('GONDAR', 'Gondar'),
        ('NAZRET', 'Nazret'),
        ('DEBRE_MARKOS', 'Debre Markos'),
        ('ARBA_MINCH', 'Arba Minch'),
    ]
    
    for code, name in cities:
        City.objects.get_or_create(name=code)

class Migration(migrations.Migration):
    dependencies = [
        ('ac', '0011_city_logisticsprofile_nationwide_order_quantity_and_more'),
    ]

    operations = [
        migrations.RunPython(load_initial_cities),
    ]