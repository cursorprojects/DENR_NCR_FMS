# Generated manually to add driver_report_attachment field to PreInspectionReport

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_change_rfid_to_separate_text_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='preinspectionreport',
            name='driver_report_attachment',
            field=models.FileField(blank=True, help_text='Driver report attachment', null=True, upload_to='pre_inspection/driver_reports/'),
        ),
    ]

