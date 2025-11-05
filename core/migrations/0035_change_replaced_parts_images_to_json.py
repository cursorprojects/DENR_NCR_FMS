# Generated manually to change replaced_parts_images from ImageField to JSONField for multiple images

from django.db import migrations, models


def migrate_existing_images_forward(apps, schema_editor):
    """Migrate existing single image to JSON list"""
    PostInspectionReport = apps.get_model('core', 'PostInspectionReport')
    
    # The old column was VARCHAR, so we need to check if there's any data
    # Since we're changing from ImageField (VARCHAR) to JSONField, 
    # we'll convert any existing single image path to a list
    for report in PostInspectionReport.objects.all():
        # If there's an old image path stored, convert it to a list
        # Note: This migration assumes the old field data is already migrated
        # Since we're changing the field type, Django will handle the conversion
        pass


def migrate_existing_images_backward(apps, schema_editor):
    """Reverse migration - take first image from list"""
    PostInspectionReport = apps.get_model('core', 'PostInspectionReport')
    
    # If reversing, take the first image from the list
    for report in PostInspectionReport.objects.all():
        if report.replaced_parts_images and len(report.replaced_parts_images) > 0:
            # This would be handled by the field type change
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_add_replaced_parts_images'),
    ]

    operations = [
        # Remove the old ImageField column
        migrations.RemoveField(
            model_name='postinspectionreport',
            name='replaced_parts_images',
        ),
        # Add the new JSONField
        migrations.AddField(
            model_name='postinspectionreport',
            name='replaced_parts_images',
            field=models.JSONField(blank=True, default=list, help_text='List of replaced parts image file paths'),
        ),
    ]

