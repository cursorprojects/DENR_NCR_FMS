from django.core.management.base import BaseCommand
from core.models import Repair, Vehicle, RepairPart, RepairPartItem, RepairShop
from decimal import Decimal
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Add sample repair data with part information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of sample repairs to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get existing data
        vehicles = list(Vehicle.objects.all())
        repair_shops = list(RepairShop.objects.filter(is_active=True))
        repair_parts = list(RepairPart.objects.filter(is_active=True))
        
        if not vehicles:
            self.stdout.write(self.style.ERROR('No vehicles found. Please add vehicles first.'))
            return
        
        if not repair_parts:
            self.stdout.write(self.style.ERROR('No repair parts found. Please run "python manage.py add_repair_parts" first.'))
            return
        
        # Sample repair parts with quantities and units
        common_parts = [
            {'part': 'Engine Oil', 'quantity': Decimal('4'), 'unit': 'liter', 'cost': Decimal('1500.00')},
            {'part': 'Oil Filter', 'quantity': Decimal('1'), 'unit': 'pcs', 'cost': Decimal('450.00')},
            {'part': 'Air Filter', 'quantity': Decimal('1'), 'unit': 'pcs', 'cost': Decimal('850.00')},
            {'part': 'Brake Pads', 'quantity': Decimal('4'), 'unit': 'pcs', 'cost': Decimal('3500.00')},
            {'part': 'Brake Discs/Rotors', 'quantity': Decimal('2'), 'unit': 'pcs', 'cost': Decimal('4500.00')},
            {'part': 'Spark Plugs', 'quantity': Decimal('4'), 'unit': 'pcs', 'cost': Decimal('1200.00')},
            {'part': 'Coolant/Antifreeze', 'quantity': Decimal('6'), 'unit': 'liter', 'cost': Decimal('1800.00')},
            {'part': 'Car Battery', 'quantity': Decimal('1'), 'unit': 'pcs', 'cost': Decimal('8500.00')},
            {'part': 'Fuel Filter', 'quantity': Decimal('1'), 'unit': 'pcs', 'cost': Decimal('650.00')},
            {'part': 'Windshield Wiper Blades', 'quantity': Decimal('2'), 'unit': 'pcs', 'cost': Decimal('450.00')},
            {'part': 'Tires', 'quantity': Decimal('4'), 'unit': 'pcs', 'cost': Decimal('12000.00')},
            {'part': 'Shock Absorbers', 'quantity': Decimal('4'), 'unit': 'pcs', 'cost': Decimal('8000.00')},
            {'part': 'Transmission Fluid', 'quantity': Decimal('8'), 'unit': 'liter', 'cost': Decimal('3200.00')},
            {'part': 'A/C Refrigerant', 'quantity': Decimal('2'), 'unit': 'kg', 'cost': Decimal('2500.00')},
            {'part': 'Power Steering Fluid', 'quantity': Decimal('2'), 'unit': 'liter', 'cost': Decimal('800.00')},
        ]
        
        # Sample descriptions
        descriptions = [
            'Regular maintenance service - oil change and filter replacement',
            'Brake system inspection and pad replacement',
            'Engine tune-up and spark plug replacement',
            'Battery replacement due to old age',
            'Tire rotation and wheel alignment',
            'Suspension check and shock absorber replacement',
            'A/C system service and refrigerant refill',
            'Transmission fluid change and inspection',
            'Major service - includes all filters and fluids',
            'Routine maintenance check and minor repairs',
            'Exhaust system inspection and muffler repair',
            'Electrical system diagnosis and repair',
            'Cooling system flush and radiator repair',
            'Fuel system cleaning and filter replacement',
            'Steering and suspension alignment service'
        ]
        
        # Sample technicians
        technicians = [
            'Juan Dela Cruz',
            'Maria Santos',
            'Pedro Garcia',
            'Ana Rodriguez',
            'Carlos Lopez',
            'Maria Clara',
            'Jose Rizal',
            'Gabriela Silva'
        ]
        
        created_count = 0
        
        for i in range(count):
            # Random vehicle
            vehicle = random.choice(vehicles)
            
            # Random date in the past 6 months
            days_ago = random.randint(1, 180)
            repair_date = datetime.now().date() - timedelta(days=days_ago)
            
            # Random status (80% completed, 20% ongoing)
            status = 'Completed' if random.random() > 0.2 else 'Ongoing'
            
            # Random description
            description = random.choice(descriptions)
            
            # Random repair shop
            repair_shop = random.choice(repair_shops) if repair_shops else None
            
            # Random technician
            technician = random.choice(technicians) if random.random() > 0.3 else ''
            
            # Create repair
            repair = Repair.objects.create(
                vehicle=vehicle,
                date_of_repair=repair_date,
                description=description,
                status=status,
                repair_shop=repair_shop,
                technician=technician,
                cost=Decimal('0'),  # Will be calculated from parts
                labor_cost=Decimal(random.randint(500, 3000))  # Random labor cost
            )
            
            # Add random number of parts (1-4 parts)
            num_parts = random.randint(1, 4)
            selected_parts = random.sample(common_parts, num_parts)
            
            total_cost = Decimal('0')
            for part_data in selected_parts:
                # Find the part by name
                part_obj = None
                for p in repair_parts:
                    if p.name == part_data['part']:
                        part_obj = p
                        break
                
                if part_obj:
                    # Create RepairPartItem
                    RepairPartItem.objects.create(
                        repair=repair,
                        part=part_obj,
                        quantity=part_data['quantity'],
                        unit=part_data['unit'],
                        cost=part_data['cost'],
                        additional_info=f'Replaced as part of maintenance'
                    )
                    total_cost += part_data['cost']
            
            # Update the repair cost with total parts cost
            repair.cost = total_cost
            repair.save()
            
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'{created_count}. Created repair for {vehicle.plate_number} - {repair_date} - '
                    f'Parts: {num_parts}, Total Cost: PHP {total_cost + repair.labor_cost:,.2f}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} sample repairs with part information!'
            )
        )
        
        self.stdout.write(f'\nTotal repairs in database: {Repair.objects.count()}')

