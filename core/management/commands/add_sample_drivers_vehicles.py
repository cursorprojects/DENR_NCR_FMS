from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Driver, Vehicle, Division, CustomUser
from decimal import Decimal
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Add sample drivers and vehicles to the database'

    def handle(self, *args, **options):
        # Get divisions
        divisions = list(Division.objects.all())
        if not divisions:
            self.stdout.write(self.style.ERROR('No divisions found. Please add divisions first.'))
            return
        
        # Sample driver data
        drivers_data = [
            {'name': 'Juan Dela Cruz', 'license_number': 'D01-123456', 'phone': '09171234567'},
            {'name': 'Maria Santos', 'license_number': 'D02-234567', 'phone': '09182345678'},
            {'name': 'Pedro Garcia', 'license_number': 'D03-345678', 'phone': '09193456789'},
            {'name': 'Ana Rodriguez', 'license_number': 'D04-456789', 'phone': '09174567890'},
            {'name': 'Carlos Lopez', 'license_number': 'D05-567890', 'phone': '09185678901'},
            {'name': 'Maria Clara Villanueva', 'license_number': 'D06-678901', 'phone': '09196789012'},
            {'name': 'Jose Rizal Mercado', 'license_number': 'D07-789012', 'phone': '09207890123'},
            {'name': 'Gabriela Silva', 'license_number': 'D08-890123', 'phone': '09218901234'},
        ]
        
        # Create drivers
        created_drivers = []
        for driver_data in drivers_data:
            driver, created = Driver.objects.get_or_create(
                license_number=driver_data['license_number'],
                defaults=driver_data
            )
            if created:
                created_drivers.append(driver)
                self.stdout.write(self.style.SUCCESS(f'Created driver: {driver.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Driver already exists: {driver.name}'))
        
        drivers = list(Driver.objects.all())
        
        # Sample vehicle data
        vehicles_data = [
            {
                'plate_number': 'ABC-1234',
                'vehicle_type': 'Sedan',
                'model': 'Vios',
                'brand': 'Toyota',
                'year': 2020,
                'engine_number': 'EN-ABC-001',
                'chassis_number': 'CN-ABC-001',
                'color': 'White',
                'acquisition_cost': Decimal('850000.00'),
                'status': 'Serviceable',
                'date_acquired': date(2020, 1, 15),
                'current_mileage': 35000,
                'rfid_type': 'Autosweep',
                'fleet_card_number': 'FC-001',
                'gas_station': 'Shell',
                'notes': 'Primary service vehicle'
            },
            {
                'plate_number': 'DEF-9012',
                'vehicle_type': 'SUV',
                'model': 'RAV4',
                'brand': 'Toyota',
                'year': 2021,
                'engine_number': 'EN-DEF-002',
                'chassis_number': 'CN-DEF-002',
                'color': 'Silver',
                'acquisition_cost': Decimal('1450000.00'),
                'status': 'Serviceable',
                'date_acquired': date(2021, 3, 20),
                'current_mileage': 28000,
                'rfid_type': 'Easytrip',
                'fleet_card_number': 'FC-002',
                'gas_station': 'Petron',
                'notes': 'Field operations vehicle'
            },
            {
                'plate_number': 'GHI-3456',
                'vehicle_type': 'Pickup Truck',
                'model': 'Hilux',
                'brand': 'Toyota',
                'year': 2019,
                'engine_number': 'EN-GHI-003',
                'chassis_number': 'CN-GHI-003',
                'color': 'Black',
                'acquisition_cost': Decimal('1250000.00'),
                'status': 'Under Repair',
                'date_acquired': date(2019, 6, 10),
                'current_mileage': 45000,
                'rfid_type': 'Autosweep',
                'fleet_card_number': 'FC-003',
                'gas_station': 'Shell',
                'notes': 'Heavy-duty vehicle'
            },
            {
                'plate_number': 'JKL-7890',
                'vehicle_type': 'Van',
                'model': 'Grandia',
                'brand': 'Toyota',
                'year': 2022,
                'engine_number': 'EN-JKL-004',
                'chassis_number': 'CN-JKL-004',
                'color': 'Blue',
                'acquisition_cost': Decimal('1380000.00'),
                'status': 'Serviceable',
                'date_acquired': date(2022, 2, 5),
                'current_mileage': 15000,
                'rfid_type': 'Easytrip',
                'fleet_card_number': 'FC-004',
                'gas_station': 'Petron',
                'notes': 'Personnel transport'
            },
            {
                'plate_number': 'XYZ-5678',
                'vehicle_type': 'Motorcycle',
                'model': 'Motorcycle 150',
                'brand': 'Honda',
                'year': 2023,
                'engine_number': 'EN-XYZ-005',
                'chassis_number': 'CN-XYZ-005',
                'color': 'Red',
                'acquisition_cost': Decimal('95000.00'),
                'status': 'Serviceable',
                'date_acquired': date(2023, 1, 10),
                'current_mileage': 8000,
                'rfid_type': None,
                'fleet_card_number': '',
                'gas_station': 'Shell',
                'notes': 'Utility motorcycle'
            },
        ]
        
        # Get a user for status tracking (use first super admin or create one)
        admin_user = CustomUser.objects.filter(role='super_admin').first()
        if not admin_user:
            admin_user = CustomUser.objects.first()
        
        # Create vehicles
        created_vehicles = []
        for vehicle_data in vehicles_data:
            # Assign random division
            vehicle_data['division'] = random.choice(divisions)
            
            # Assign random driver (50% chance)
            if random.random() > 0.5 and drivers:
                vehicle_data['assigned_driver'] = random.choice(drivers)
            else:
                vehicle_data['assigned_driver'] = None
            
            # Add status tracking fields
            vehicle_data['status_changed_at'] = timezone.now() - timedelta(days=random.randint(1, 30))
            vehicle_data['status_changed_by'] = admin_user
            vehicle_data['status_change_reason'] = f'Initial status set to {vehicle_data["status"]} during sample data creation'
            
            vehicle, created = Vehicle.objects.get_or_create(
                plate_number=vehicle_data['plate_number'],
                defaults=vehicle_data
            )
            if created:
                created_vehicles.append(vehicle)
                driver_info = f' - Driver: {vehicle.assigned_driver.name}' if vehicle.assigned_driver else ''
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created vehicle: {vehicle.plate_number} '
                        f'({vehicle.brand} {vehicle.model}){driver_info}'
                    )
                )
            else:
                self.stdout.write(self.style.WARNING(f'Vehicle already exists: {vehicle.plate_number}'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully added {len(created_vehicles)} new vehicles!'
            )
        )
        
        self.stdout.write(f'\nTotal vehicles in database: {Vehicle.objects.count()}')
        self.stdout.write(f'Total drivers in database: {Driver.objects.count()}')

