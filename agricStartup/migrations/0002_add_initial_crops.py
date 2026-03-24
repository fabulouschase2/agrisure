from django.db import migrations

def add_crops(apps, schema_editor):
    Crop = apps.get_model('agricStartup', 'Crop')
    crops = [
        {'name': 'Maize', 'average_yield_per_hectare': 3.0, 'market_price_per_ton': 50000},
        {'name': 'Rice', 'average_yield_per_hectare': 4.0, 'market_price_per_ton': 60000},
        {'name': 'Cassava', 'average_yield_per_hectare': 10.0, 'market_price_per_ton': 20000},
        {'name': 'Soybean', 'average_yield_per_hectare': 2.5, 'market_price_per_ton': 55000},
    ]
    for crop in crops:
        Crop.objects.create(**crop)

class Migration(migrations.Migration):
    dependencies = [
        ('agricStartup', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(add_crops),
    ]