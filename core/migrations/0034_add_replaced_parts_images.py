# Generated manually to add replaced_parts_images field to PostInspectionReport

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_add_driver_report_attachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='postinspectionreport',
            name='replaced_parts_images',
            field=models.ImageField(blank=True, help_text='Images of replaced parts', null=True, upload_to='post_inspection/replaced_parts/'),
        ),
    ]

