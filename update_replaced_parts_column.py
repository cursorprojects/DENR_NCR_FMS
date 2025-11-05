#!/usr/bin/env python
"""
Script to update replaced_parts_images column from VARCHAR to JSON type.
Run this from the project directory.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleetmanagement.settings')
django.setup()

from django.db import connection

def update_column_to_json():
    """Update replaced_parts_images column from VARCHAR to JSON type"""
    with connection.cursor() as cursor:
        try:
            print("Checking current column type...")
            cursor.execute("""
                SELECT COLUMN_TYPE, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_postinspectionreport' 
                AND COLUMN_NAME = 'replaced_parts_images'
            """)
            result = cursor.fetchone()
            if result:
                print(f"Current column type: {result[0]} ({result[1]})")
                
                # If it's already JSON, skip
                if result[1].lower() in ['json', 'longtext']:
                    print("✓ Column is already JSON/LONGTEXT type")
                    return
                
            print("\nUpdating replaced_parts_images column to JSON type...")
            
            # First, migrate any existing single image path to JSON array format
            print("Migrating existing data...")
            cursor.execute("""
                UPDATE core_postinspectionreport 
                SET replaced_parts_images = CASE 
                    WHEN replaced_parts_images IS NULL OR replaced_parts_images = '' THEN '[]'
                    WHEN replaced_parts_images NOT LIKE '[%' THEN CONCAT('["', replaced_parts_images, '"]')
                    ELSE replaced_parts_images
                END
            """)
            
            # Change column type to JSON
            print("Changing column type to JSON...")
            cursor.execute("""
                ALTER TABLE `core_postinspectionreport` 
                MODIFY COLUMN `replaced_parts_images` JSON NULL DEFAULT NULL
            """)
            
            print("✓ Successfully updated replaced_parts_images column to JSON type")
            
            # Verify the change
            cursor.execute("""
                SELECT COLUMN_TYPE, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'core_postinspectionreport' 
                AND COLUMN_NAME = 'replaced_parts_images'
            """)
            result = cursor.fetchone()
            if result:
                print(f"✓ Verified: Column type is now {result[0]} ({result[1]})")
                
        except Exception as e:
            if "Duplicate column name" in str(e) or "already exists" in str(e):
                print(f"✓ Column already in correct format")
            else:
                print(f"✗ Error: {e}")
                import traceback
                traceback.print_exc()

if __name__ == '__main__':
    update_column_to_json()

