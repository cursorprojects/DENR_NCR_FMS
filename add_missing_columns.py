#!/usr/bin/env python
"""
Script to add missing database columns using Django's database connection.
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

def add_missing_columns():
    """Add missing columns to the database"""
    with connection.cursor() as cursor:
        try:
            # Add driver_report_attachment to PreInspectionReport
            print("Adding driver_report_attachment column to core_preinspectionreport...")
            cursor.execute("""
                ALTER TABLE `core_preinspectionreport` 
                ADD COLUMN `driver_report_attachment` VARCHAR(100) NULL DEFAULT NULL 
                AFTER `photos`
            """)
            print("✓ Successfully added driver_report_attachment column")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("✓ driver_report_attachment column already exists")
            else:
                print(f"✗ Error adding driver_report_attachment: {e}")
        
        try:
            # Add replaced_parts_images to PostInspectionReport
            print("\nAdding replaced_parts_images column to core_postinspectionreport...")
            cursor.execute("""
                ALTER TABLE `core_postinspectionreport` 
                ADD COLUMN `replaced_parts_images` VARCHAR(100) NULL DEFAULT NULL 
                AFTER `photos`
            """)
            print("✓ Successfully added replaced_parts_images column")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("✓ replaced_parts_images column already exists")
            else:
                print(f"✗ Error adding replaced_parts_images: {e}")
        
        print("\n✓ Database columns updated successfully!")

if __name__ == '__main__':
    add_missing_columns()

