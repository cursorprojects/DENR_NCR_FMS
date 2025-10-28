from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Driver, Vehicle, Division, PMS
from decimal import Decimal
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Add vehicles specifically designed to test the "Vehicles Near PMS" dashboard feature'

    def handle(self, *args, **options):
        # Get divisions
        divisions = list(Division.objects.all())
        if not divisions:
            self.stdout.write(self.style.ERROR('No divisions found. Please add divisions first.'))
            return
        
        # Get drivers
        drivers = list(Driver.objects.all())
        if not drivers:
            self.stdout.write(self.style.ERROR('No drivers found. Please add drivers first.'))
            return

        # Vehicles that will appear in "Vehicles Near PMS" table
        pms_test_vehicles = [
            # Vehicle 1: No PMS record ever (highest priority)
            {
                'plate_number': 'PMS-0001',
                'vehicle_type': 'Sedan',
                'model': 'Altis',
                'brand': 'Toyota',
                'year': 2022,
                'engine_number': 'EN-PMS-001',
                'chassis_number': 'CN-PMS-001',
                'color': 'White',
                'acquisition_cost': Decimal('1200000.00'),
                'status': 'Serviceable',
                'date_acquired': date(2022, 1, 15),
                'current_mileage': 25000,
                'rfid_type': 'Autosweep',
                'fleet_card_number': 'FC-PMS-001',
                'gas_station': 'Shell',
                'notes': 'Never had PMS - should appear first in list',
                'pms_scenario': 'no_pms'
            },
            # Vehicle 2: 6+ months since last PMS
            {
                'plate_number': 'PMS-0002',
                'vehicle_type': 'SUV',
                'model': 'Fortuner',
                'brand': 'Toyota',
                'year': 2021,
                'engine_number': 'EN-PMS-002',
                'chassis_number': 'CN-PMS-002',
                'color': 'Black',
                'acquisition_cost': Decimal('1800000.00'),
                'status': 'Serviceable',
                'date_acquired': date(2021, 3, 20),
                'current_mileage': 45000,
                'rfid_type': 'Easytrip',
                'fleet_card_number': 'FC-PMS-002',
                'gas_station': 'Petron',
                'notes': 'Last PMS 8 months ago - overdue',
                'pms_scenario': 'overdue_time',
                'last_pms_date': date(2024, 3, 15),  # 8 months ago
                'last_pms_mileage': 38000,
                'next_service_mileage': 48000
            },
            # Vehicle 3: Reached next service mileage
            {
                'plate_number': 'PMS-0003',
                'vehicle_type': 'Pickup Truck',
                'model': 'Ranger',
                'brand': 'Ford',
                'year': 2020,
                'engine_number': 'EN-PMS-003',
                'chassis_number': 'CN-PMS-003',
                'color': 'Blue',
                'acquisition_cost': Decimal('1500000.00'),
                'status': 'Serviceable',
                'date_acquired': date(2020, 6, 10),
                'current_mileage': 55000,
                'rfid_type': 'Autosweep',
                'fleet_card_number': 'FC-PMS-003',
                'gas_station': 'Shell',
                'notes': 'Reached 50,000km service interval',
                'pms_scenario': 'overdue_mileage',
                'last_pms_date': date(2024, 6, 15),  # 4 months ago
                'last_pms_mileage': 45000,
                'next_service_mileage': 50000
            },
            # Vehicle 4: Close to 6 months (borderline case)
            {
                'plate_number': 'PMS-0004',
                'vehicle_type': 'Van',
                'model': 'Hiace',
                'brand': 'Toyota',
                'year': 2023,
                'engine_number': 'EN-PMS-004',
                'chassis_number': 'CN-PMS-004',
                'color': 'Silver',
                'acquisition_cost': Decimal('1600000.00'),
                'status': 'Serviceable',
                'date_acquired': date(2023, 2, 5),
                'current_mileage': 18000,
                'rfid_type': 'Easytrip',
                'fleet_card_number': 'FC-PMS-004',
                'gas_station': 'Petron',
                'notes': 'Last PMS 5.5 months ago - approaching limit',
                'pms_scenario': 'approaching_time',
                'last_pms_date': date(2024, 5, 1),  # 5.5 months ago
                'last_pms_mileage': 15000,
                'next_service_mileage': 25000
            },
            # Vehicle 5: High mileage since last PMS
            {
                'plate_number': 'PMS-0005',
                'vehicle_type': 'Motorcycle',
                'model': 'Wave 125',
                'brand': 'Honda',
                'year': 2022,
                'engine_number': 'EN-PMS-005',
                'chassis_number': 'CN-PMS-005',
                'color': 'Red',
                'acquisition_cost': Decimal('80000.00'),
                'status': 'Serviceable',
                'date_acquired': date(2022, 4, 10),
                'current_mileage': 35000,
                'rfid_type': None,
                'fleet_card_number': '',
                'gas_station': 'Shell',
                'notes': 'High mileage motorcycle - 12,000km since last PMS',
                'pms_scenario': 'high_mileage',
                'last_pms_date': date(2024, 4, 1),  # 3 months ago
                'last_pms_mileage': 23000,
                'next_service_mileage': 28000
            },
            # Vehicle 6: Another no PMS case
            {
                'plate_number': 'PMS-0006',
                'vehicle_type': 'Sedan',
                'model': 'Civic',
                'brand': 'Honda',
                'year': 2023,
                'engine_number': 'EN-PMS-006',
                'chassis_number': 'CN-PMS-006',
                'color': 'Gray',
                'acquisition_cost': Decimal('1100000.00'),
                'status': 'Serviceable',
                'date_acquired': date(2023, 8, 20),
                'current_mileage': 12000,
                'rfid_type': 'Autosweep',
                'fleet_card_number': 'FC-PMS-006',
                'gas_station': 'Shell',
                'notes': 'New vehicle - no PMS scheduled yet',
                'pms_scenario': 'no_pms'
            }
        ]

        created_vehicles = []
        created_pms_records = []

        for vehicle_data in pms_test_vehicles:
            # Extract PMS scenario data
            pms_scenario = vehicle_data.pop('pms_scenario')
            last_pms_date = vehicle_data.pop('last_pms_date', None)
            last_pms_mileage = vehicle_data.pop('last_pms_mileage', None)
            next_service_mileage = vehicle_data.pop('next_service_mileage', None)

            # Assign random division and driver
            vehicle_data['division'] = random.choice(divisions)
            vehicle_data['assigned_driver'] = random.choice(drivers)

            # Create vehicle
            vehicle, created = Vehicle.objects.get_or_create(
                plate_number=vehicle_data['plate_number'],
                defaults=vehicle_data
            )
            
            if created:
                created_vehicles.append(vehicle)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created vehicle: {vehicle.plate_number} '
                        f'({vehicle.brand} {vehicle.model}) - Scenario: {pms_scenario}'
                    )
                )

                # Create PMS record if needed (for scenarios other than 'no_pms')
                if pms_scenario != 'no_pms' and last_pms_date:
                    pms = PMS.objects.create(
                        vehicle=vehicle,
                        service_type='General Inspection',
                        scheduled_date=last_pms_date,
                        completed_date=last_pms_date + timedelta(days=1),
                        mileage_at_service=last_pms_mileage,
                        next_service_mileage=next_service_mileage,
                        cost=Decimal('1500.00'),
                        provider='Test Auto Service',
                        technician='Test Technician',
                        description='Test PMS record for dashboard testing',
                        notes='This is a test PMS record',
                        status='Completed'
                    )
                    created_pms_records.append(pms)
                    self.stdout.write(
                        f'  -> Created PMS record: {last_pms_date} at {last_pms_mileage:,}km'
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Vehicle already exists: {vehicle.plate_number}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {len(created_vehicles)} test vehicles!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(created_pms_records)} PMS records!'
            )
        )
        
        self.stdout.write('\nTest Vehicle Scenarios:')
        self.stdout.write('  PMS-0001: No PMS record (highest priority)')
        self.stdout.write('  PMS-0002: 8 months since last PMS (overdue)')
        self.stdout.write('  PMS-0003: Reached 50,000km service interval')
        self.stdout.write('  PMS-0004: 5.5 months since last PMS (approaching limit)')
        self.stdout.write('  PMS-0005: High mileage motorcycle (12,000km since PMS)')
        self.stdout.write('  PMS-0006: New vehicle with no PMS')
        
        self.stdout.write(f'\nTotal vehicles in database: {Vehicle.objects.count()}')
        self.stdout.write(f'Total PMS records in database: {PMS.objects.count()}')
        
        self.stdout.write(
            self.style.SUCCESS(
                '\nThese vehicles should now appear in the "Vehicles Near PMS" dashboard table!'
            )
        )
