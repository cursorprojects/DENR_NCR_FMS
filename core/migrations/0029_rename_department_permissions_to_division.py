# Generated manually to rename department permissions to division permissions

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_alter_vehicle_status_alter_vehicle_vehicle_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='can_view_departments',
            new_name='can_view_divisions',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='can_add_departments',
            new_name='can_add_divisions',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='can_edit_departments',
            new_name='can_edit_divisions',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='can_delete_departments',
            new_name='can_delete_divisions',
        ),
    ]

