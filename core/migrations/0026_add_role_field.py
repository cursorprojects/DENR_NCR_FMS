# Generated manually to add missing role field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_add_inspection_reports'),
    ]

    operations = [
        # Use RunSQL to conditionally add the role field if it doesn't exist
        migrations.RunSQL(
            # MySQL/MariaDB specific: Check and add column if not exists
            """
            SET @dbname = DATABASE();
            SET @tablename = 'core_customuser';
            SET @columnname = 'role';
            SET @preparedStatement = (SELECT IF(
              (
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE
                  (TABLE_SCHEMA = @dbname)
                  AND (TABLE_NAME = @tablename)
                  AND (COLUMN_NAME = @columnname)
              ) > 0,
              'SELECT 1;',
              CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' VARCHAR(20) DEFAULT ''encoder'';')
            ));
            PREPARE stmt FROM @preparedStatement;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            # Reverse SQL
            "ALTER TABLE core_customuser DROP COLUMN IF EXISTS role;",
        ),
    ]
