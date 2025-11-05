# Generated manually to add current_market_value field to Vehicle model

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_rename_department_permissions_to_division'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='current_market_value',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Current Market Value'),
        ),
    ]

