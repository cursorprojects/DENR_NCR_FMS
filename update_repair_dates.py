#!/usr/bin/env python
"""Script to update repair dates to span the last 12 months"""
import os
import django
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleetmanagement.settings')
django.setup()

from core.models import Repair

def update_repair_dates():
    print("Updating repair dates to span the last 12 months...")
    
    repairs = Repair.objects.all().order_by('date_of_repair')
    total_repairs = repairs.count()
    
    if total_repairs == 0:
        print("No repair records found to update.")
        return
    
    # Group repairs by their position and assign to last 12 months
    for idx, repair in enumerate(repairs):
        # Distribute evenly across last 12 months
        months_back = 11 - (idx % 12)
        
        # Calculate the date N months ago
        target_date = date.today() - relativedelta(months=months_back)
        
        repair.date_of_repair = target_date
        repair.save()
    
    print(f"Updated {total_repairs} repair records with dates from the last 12 months.")
    print("Sample dates:")
    for repair in repairs[:5]:
        print(f"  {repair.date_of_repair} - {repair.description[:50]}")

if __name__ == '__main__':
    update_repair_dates()
