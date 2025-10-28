from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import PMS, Vehicle
import random


class Command(BaseCommand):
    help = 'Add sample PMS records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of PMS records to create (default: 20)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get all vehicles
        vehicles = Vehicle.objects.all()
        if not vehicles.exists():
            self.stdout.write(
                self.style.WARNING('No vehicles found. Please add vehicles first.')
            )
            return

        # Service types (now only General Inspection)
        service_type = 'General Inspection'
        
        # Status choices
        status_choices = ['Scheduled', 'In Progress', 'Completed', 'Overdue', 'Cancelled']
        
        # Sample service providers (repair shops)
        providers = [
            'AutoCare Service Center',
            'Quick Fix Garage',
            'Professional Auto Repair',
            'Reliable Motors',
            'Express Service Station',
            'Precision Auto Works',
            'City Garage',
            'Metro Auto Service'
        ]
        
        # Sample technicians
        technicians = [
            'Juan Dela Cruz',
            'Pedro Santos',
            'Maria Garcia',
            'Jose Rodriguez',
            'Ana Martinez',
            'Carlos Lopez',
            'Elena Fernandez',
            'Miguel Torres'
        ]
        
        # Sample descriptions
        descriptions = [
            'Routine general inspection including engine, brakes, lights, and fluid levels.',
            'Comprehensive vehicle inspection covering all major systems and components.',
            'Standard PMS check including oil, filters, belts, and safety systems.',
            'Complete vehicle assessment for roadworthiness and performance.',
            'Regular maintenance inspection with detailed component analysis.',
            'Full vehicle check-up including engine diagnostics and safety inspection.',
            'Comprehensive PMS covering all vehicle systems and safety features.',
            'Routine inspection with focus on preventive maintenance items.'
        ]
        
        # Sample notes
        notes_samples = [
            'Vehicle in good condition. All systems functioning properly.',
            'Minor adjustments made to brake system. No major issues found.',
            'Fluid levels topped up. Battery tested and in good condition.',
            'Tire pressure adjusted. All lights working correctly.',
            'Engine running smoothly. No unusual noises detected.',
            'All safety systems checked and functioning properly.',
            'Vehicle ready for continued service. Next inspection recommended in 3 months.',
            'Minor wear noted on brake pads. Monitor for next service.'
        ]

        created_count = 0
        
        for i in range(count):
            # Select random vehicle
            vehicle = random.choice(vehicles)
            
            # Generate random dates
            base_date = datetime.now() - timedelta(days=random.randint(30, 365))
            scheduled_date = base_date.date()
            
            # Randomly determine if completed
            is_completed = random.choice([True, False, True])  # 2/3 chance of completion
            
            if is_completed:
                completed_date = scheduled_date + timedelta(days=random.randint(0, 7))
                status = random.choice(['Completed'])
            else:
                completed_date = None
                if scheduled_date < datetime.now().date():
                    status = random.choice(['Overdue', 'Scheduled'])
                else:
                    status = random.choice(['Scheduled', 'In Progress'])
            
            # Generate mileage (use vehicle's current mileage as base)
            base_mileage = vehicle.current_mileage or 0
            mileage_at_service = max(0, base_mileage - random.randint(1000, 5000))
            
            # Generate next service mileage
            next_service_mileage = mileage_at_service + random.randint(5000, 15000)
            
            # Generate cost (some records may not have cost yet)
            cost = None
            if is_completed:
                cost = round(random.uniform(500, 3000), 2)
            
            # Select random provider and technician
            provider = random.choice(providers)
            technician = random.choice(technicians)
            
            # Select random description and notes
            description = random.choice(descriptions)
            notes = random.choice(notes_samples) if is_completed else ''
            
            try:
                pms = PMS.objects.create(
                    vehicle=vehicle,
                    service_type=service_type,
                    scheduled_date=scheduled_date,
                    completed_date=completed_date,
                    mileage_at_service=mileage_at_service,
                    next_service_mileage=next_service_mileage,
                    cost=cost,
                    provider=provider,
                    technician=technician,
                    description=description,
                    notes=notes,
                    status=status
                )
                
                created_count += 1
                self.stdout.write(
                    f'Created PMS record for {vehicle.plate_number} - {scheduled_date} ({status})'
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating PMS record: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} PMS records')
        )
