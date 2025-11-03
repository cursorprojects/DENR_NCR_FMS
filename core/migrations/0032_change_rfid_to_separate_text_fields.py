# Generated manually to change RFID from boolean fields to separate text fields

from django.db import migrations, models


def migrate_rfid_data_forward(apps, schema_editor):
    Vehicle = apps.get_model('core', 'Vehicle')
    # Migrate RFID numbers based on boolean flags
    # If has_autosweep was True, try to preserve RFID number or create one
    for vehicle in Vehicle.objects.filter(has_autosweep=True):
        if not vehicle.rfid_autosweep_number and vehicle.rfid_number:
            # Use existing RFID number if available
            vehicle.rfid_autosweep_number = vehicle.rfid_number
        vehicle.save()
    
    for vehicle in Vehicle.objects.filter(has_easytrip=True):
        if not vehicle.rfid_easytrip_number and vehicle.rfid_number and not vehicle.has_autosweep:
            # Use existing RFID number if only Easytrip is set
            vehicle.rfid_easytrip_number = vehicle.rfid_number
        vehicle.save()


def migrate_rfid_data_backward(apps, schema_editor):
    Vehicle = apps.get_model('core', 'Vehicle')
    # Reverse migration - set boolean flags if numbers exist
    Vehicle.objects.filter(rfid_autosweep_number__isnull=False).exclude(rfid_autosweep_number='').update(has_autosweep=True)
    Vehicle.objects.filter(rfid_easytrip_number__isnull=False).exclude(rfid_easytrip_number='').update(has_easytrip=True)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_change_rfid_type_to_boolean_fields'),
    ]

    operations = [
        # Add new RFID number fields
        migrations.AddField(
            model_name='vehicle',
            name='rfid_autosweep_number',
            field=models.CharField(blank=True, max_length=100, verbose_name='Autosweep RFID Number'),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='rfid_easytrip_number',
            field=models.CharField(blank=True, max_length=100, verbose_name='Easytrip RFID Number'),
        ),
        # Migrate data from old fields
        migrations.RunPython(
            code=migrate_rfid_data_forward,
            reverse_code=migrate_rfid_data_backward,
        ),
        # Remove old fields
        migrations.RemoveField(
            model_name='vehicle',
            name='rfid_number',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='has_autosweep',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='has_easytrip',
        ),
    ]

