#!/usr/bin/env python
"""
Script to fix any invalid JSON data in replaced_parts_images field.
Run this from the project directory.
"""
import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleetmanagement.settings')
django.setup()

from core.models import PostInspectionReport
from django.db import connection

def fix_json_field_data():
    """Fix any invalid JSON data in replaced_parts_images field"""
    try:
        # Get all PostInspectionReport objects
        reports = PostInspectionReport.objects.all()
        fixed_count = 0
        
        for report in reports:
            try:
                # Try to access the field - this will fail if JSON is invalid
                images = report.replaced_parts_images
                
                # If it's not a list, convert it
                if images is None:
                    report.replaced_parts_images = []
                    report.save(update_fields=['replaced_parts_images'])
                    fixed_count += 1
                    print(f"Fixed report {report.id}: Set to empty list")
                elif not isinstance(images, list):
                    # If it's a string, try to parse it
                    if isinstance(images, str):
                        try:
                            parsed = json.loads(images)
                            if isinstance(parsed, list):
                                report.replaced_parts_images = parsed
                            else:
                                report.replaced_parts_images = [parsed] if parsed else []
                            report.save(update_fields=['replaced_parts_images'])
                            fixed_count += 1
                            print(f"Fixed report {report.id}: Converted string to list")
                        except:
                            report.replaced_parts_images = []
                            report.save(update_fields=['replaced_parts_images'])
                            fixed_count += 1
                            print(f"Fixed report {report.id}: Invalid JSON, set to empty list")
                    else:
                        # Convert other types to list
                        report.replaced_parts_images = [str(images)] if images else []
                        report.save(update_fields=['replaced_parts_images'])
                        fixed_count += 1
                        print(f"Fixed report {report.id}: Converted to list")
            except Exception as e:
                print(f"Error processing report {report.id}: {str(e)}")
                # Try to fix by setting to empty list
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE core_postinspectionreport 
                            SET replaced_parts_images = '[]' 
                            WHERE id = %s
                        """, [report.id])
                    print(f"Fixed report {report.id}: Set to empty list via SQL")
                    fixed_count += 1
                except Exception as sql_error:
                    print(f"Could not fix report {report.id} via SQL: {str(sql_error)}")
        
        print(f"\n✓ Fixed {fixed_count} report(s)")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_json_field_data()

