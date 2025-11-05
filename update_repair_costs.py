#!/usr/bin/env python
"""Script to update repair costs to 3-4 digit amounts"""
import os
import django
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleetmanagement.settings')
django.setup()

from core.models import Repair

def update_repair_costs():
    print("Updating repair costs to 3-4 digit amounts...")
    
    repairs = Repair.objects.all()
    total_repairs = repairs.count()
    
    if total_repairs == 0:
        print("No repair records found to update.")
        return
    
    # Define realistic cost ranges for different types of repairs
    # Costs in Philippine Peso (₱) - 4 to 5 digits
    cost_ranges = [
        (Decimal('1500.00'), Decimal('4500.00')),  # Basic maintenance
        (Decimal('5000.00'), Decimal('15000.00')),  # Moderate repairs
        (Decimal('16000.00'), Decimal('35000.00')),  # Major repairs
        (Decimal('40000.00'), Decimal('95000.00')),  # Significant repairs
    ]
    
    updated_count = 0
    for repair in repairs:
        # Randomly select a cost range
        selected_range = random.choice(cost_ranges)
        
        # Generate a random cost within the selected range
        min_cost, max_cost = selected_range
        # Generate cost in 50 peso increments for realistic pricing
        cost_increment = Decimal('50.00')
        num_increments = int((max_cost - min_cost) / cost_increment)
        random_increments = random.randint(0, num_increments)
        new_cost = min_cost + (Decimal(random_increments) * cost_increment)
        
        repair.cost = new_cost
        repair.save()
        updated_count += 1
        
        if updated_count <= 5:
            print(f"  {repair.description[:40]:40s} - PHP {new_cost}")
    
    print(f"\nUpdated {updated_count} repair records with 4-5 digit costs.")
    print("Costs range from PHP 1,500 to PHP 95,000")

if __name__ == '__main__':
    update_repair_costs()
