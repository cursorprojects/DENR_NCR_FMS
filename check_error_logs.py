#!/usr/bin/env python
"""
Script to check Django error logs and identify the specific error.
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
from core.models import PostInspectionReport, Vehicle, Repair, PMS
import traceback

def check_database_issues():
    """Check for database-related issues"""
    print("Checking database connections...")
    
    try:
        # Test Vehicle query
        print("Testing Vehicle.objects.count()...")
        count = Vehicle.objects.count()
        print(f"✓ Vehicle count: {count}")
    except Exception as e:
        print(f"✗ Vehicle query error: {e}")
        traceback.print_exc()
    
    try:
        # Test PostInspectionReport query
        print("\nTesting PostInspectionReport queries...")
        reports = PostInspectionReport.objects.all()[:5]
        print(f"✓ Found {len(reports)} reports")
        
        for report in reports:
            try:
                images = report.get_replaced_parts_images_list()
                print(f"  ✓ Report {report.id}: {len(images)} images")
            except Exception as e:
                print(f"  ✗ Report {report.id} error: {e}")
    except Exception as e:
        print(f"✗ PostInspectionReport query error: {e}")
        traceback.print_exc()
    
    try:
        # Test Repair query
        print("\nTesting Repair.objects.all()...")
        repairs = Repair.objects.all()[:5]
        print(f"✓ Found {len(repairs)} repairs")
    except Exception as e:
        print(f"✗ Repair query error: {e}")
        traceback.print_exc()
    
    try:
        # Test PMS query
        print("\nTesting PMS.objects.filter()...")
        pms_list = PMS.objects.filter(status__in=['Scheduled', 'Overdue'])[:5]
        print(f"✓ Found {len(pms_list)} PMS records")
    except Exception as e:
        print(f"✗ PMS query error: {e}")
        traceback.print_exc()

def check_json_fields():
    """Check for invalid JSON in replaced_parts_images"""
    print("\n" + "="*50)
    print("Checking JSON fields...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, replaced_parts_images, 
                       JSON_VALID(replaced_parts_images) as is_valid
                FROM core_postinspectionreport
                LIMIT 10
            """)
            results = cursor.fetchall()
            
            invalid_count = 0
            for row in results:
                report_id, json_data, is_valid = row
                if is_valid == 0:
                    invalid_count += 1
                    print(f"✗ Report {report_id} has invalid JSON: {json_data}")
            
            if invalid_count == 0:
                print("✓ All JSON fields are valid")
            else:
                print(f"✗ Found {invalid_count} invalid JSON fields")
    except Exception as e:
        print(f"✗ Error checking JSON: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    print("="*50)
    print("Django Error Diagnostic Tool")
    print("="*50)
    check_database_issues()
    check_json_fields()
    print("\n" + "="*50)
    print("Diagnostic complete!")

