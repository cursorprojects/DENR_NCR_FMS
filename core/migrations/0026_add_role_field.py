# Generated manually to add missing role field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_add_inspection_reports'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('super_admin', 'Super Admin'), ('fleet_manager', 'Fleet Manager'), ('encoder', 'Encoder/Staff')], default='encoder', max_length=20),
        ),
    ]
