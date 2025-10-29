from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Vehicle, CustomUser, Repair, PMS
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Create sample status changes and related records to demonstrate the new status tracking system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of vehicles to create sample data for (default: 5)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get vehicles and users
        vehicles = list(Vehicle.objects.all())
        users = list(CustomUser.objects.all())
        
        if not vehicles:
            self.stdout.write(
                self.style.ERROR('No vehicles found. Please add vehicles first.')
            )
            return
        
        if not users:
            self.stdout.write(
                self.style.ERROR('No users found. Please create users first.')
            )
            return
        
        # Select random vehicles
        selected_vehicles = random.sample(vehicles, min(count, len(vehicles)))
        
        created_records = {
            'repairs': 0,
            'pms': 0,
            'status_changes': 0
        }
        
        for vehicle in selected_vehicles:
            self.stdout.write(f'\nProcessing vehicle: {vehicle.plate_number}')
            
            # Create sample repair records with different statuses
            repair_scenarios = [
                {
                    'status': 'Ongoing',
                    'description': 'Engine maintenance in progress',
                    'cost': 5000.00,
                    'days_ago': 5
                },
                {
                    'status': 'Completed',
                    'description': 'Brake pad replacement completed',
                    'cost': 3000.00,
                    'days_ago': 15
                }
            ]
            
            for scenario in repair_scenarios:
                repair_date = timezone.now().date() - timedelta(days=scenario['days_ago'])
                
                repair = Repair.objects.create(
                    vehicle=vehicle,
                    date_of_repair=repair_date,
                    description=scenario['description'],
                    cost=scenario['cost'],
                    repair_shop=None,  # Will be set if repair shops exist
                    technician='Sample Technician',
                    status=scenario['status']
                )
                created_records['repairs'] += 1
                
                self.stdout.write(f'  Created repair: {scenario["status"]} - {scenario["description"]}')
            
            # Create sample PMS records
            pms_scenarios = [
                {
                    'status': 'In Progress',
                    'service_type': 'General Inspection',
                    'days_ago': 3
                },
                {
                    'status': 'Completed',
                    'service_type': 'Oil Change',
                    'days_ago': 20
                }
            ]
            
            for scenario in pms_scenarios:
                scheduled_date = timezone.now().date() - timedelta(days=scenario['days_ago'])
                completed_date = scheduled_date + timedelta(days=1) if scenario['status'] == 'Completed' else None
                
                pms = PMS.objects.create(
                    vehicle=vehicle,
                    service_type=scenario['service_type'],
                    scheduled_date=scheduled_date,
                    completed_date=completed_date,
                    mileage_at_service=vehicle.current_mileage - random.randint(1000, 5000),
                    next_service_mileage=vehicle.current_mileage + random.randint(5000, 10000),
                    cost=random.randint(1000, 3000),
                    provider='Sample Service Center',
                    technician='Sample PMS Technician',
                    description=f'Sample {scenario["service_type"]} for testing',
                    notes='Sample PMS record for status tracking demonstration',
                    status=scenario['status']
                )
                created_records['pms'] += 1
                
                self.stdout.write(f'  Created PMS: {scenario["status"]} - {scenario["service_type"]}')
            
            # Create a manual status change
            old_status = vehicle.status
            new_status = random.choice(['Serviceable', 'Under Repair', 'Unserviceable'])
            
            if new_status != old_status:
                vehicle.update_status(
                    new_status=new_status,
                    user=random.choice(users),
                    reason=f'Sample status change for demonstration - changed from {old_status} to {new_status}'
                )
                created_records['status_changes'] += 1
                
                self.stdout.write(f'  Updated status: {old_status} → {new_status}')
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSample data creation complete!'
            )
        )
        self.stdout.write(f'Processed {len(selected_vehicles)} vehicles')
        self.stdout.write(f'Created {created_records["repairs"]} repair records')
        self.stdout.write(f'Created {created_records["pms"]} PMS records')
        self.stdout.write(f'Created {created_records["status_changes"]} status changes')
        
        self.stdout.write(
            self.style.SUCCESS(
                '\nYou can now test the status tracking features:'
            )
        )
        self.stdout.write('  - View vehicle detail pages to see status change history')
        self.stdout.write('  - Use the "Change Status" button to manually update status')
        self.stdout.write('  - Check notifications for status change alerts')
        self.stdout.write('  - Observe automatic status updates from repairs/PMS')
