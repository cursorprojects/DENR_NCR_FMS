# Generated manually to change rfid_type from single choice to separate boolean fields

from django.db import migrations, models


def migrate_rfid_data_forward(apps, schema_editor):
    Vehicle = apps.get_model('core', 'Vehicle')
    # Set has_autosweep for vehicles with Autosweep
    Vehicle.objects.filter(rfid_type='Autosweep').update(has_autosweep=True)
    # Set has_easytrip for vehicles with Easytrip
    Vehicle.objects.filter(rfid_type='Easytrip').update(has_easytrip=True)


def migrate_rfid_data_backward(apps, schema_editor):
    Vehicle = apps.get_model('core', 'Vehicle')
    # This is a simplified reverse - we can't fully restore since both could be true
    # Set Autosweep if only Autosweep is checked
    Vehicle.objects.filter(has_autosweep=True, has_easytrip=False).update(rfid_type='Autosweep')
    # Set Easytrip if only Easytrip is checked
    Vehicle.objects.filter(has_easytrip=True, has_autosweep=False).update(rfid_type='Easytrip')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_add_vehicle_current_market_value'),
    ]

    operations = [
        # Add new boolean fields
        migrations.AddField(
            model_name='vehicle',
            name='has_autosweep',
            field=models.BooleanField(default=False, verbose_name='Has Autosweep RFID'),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='has_easytrip',
            field=models.BooleanField(default=False, verbose_name='Has Easytrip RFID'),
        ),
        # Migrate data from old rfid_type to new fields
        migrations.RunPython(
            code=migrate_rfid_data_forward,
            reverse_code=migrate_rfid_data_backward,
        ),
        # Remove old rfid_type field
        migrations.RemoveField(
            model_name='vehicle',
            name='rfid_type',
        ),
    ]

