from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import (
    Division, Driver, Vehicle, RepairShop, RepairPart, Repair, 
    PMS, PreInspectionReport, PostInspectionReport, Notification, 
    RepairPartItem, CustomUser
)
from datetime import datetime, timedelta
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Add ALL test data to the database - comprehensive sample data for Fleet Management System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip creating items that already exist',
        )

    def handle(self, *args, **options):
        skip_existing = options.get('skip_existing', False)
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('FLEET MANAGEMENT SYSTEM - TEST DATA CREATION'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # Step 1: Create users with admin permissions
        self.stdout.write('\n[1/11] Creating users...')
        self.create_users()
        
        # Step 2: Create divisions
        self.stdout.write('\n[2/11] Creating divisions...')
        self.create_divisions()
        
        # Step 3: Create drivers
        self.stdout.write('\n[3/11] Creating drivers...')
        self.create_drivers()
        
        # Step 4: Create vehicles
        self.stdout.write('\n[4/11] Creating vehicles...')
        self.create_vehicles()
        
        # Step 5: Create repair shops
        self.stdout.write('\n[5/11] Creating repair shops...')
        self.create_repair_shops()
        
        # Step 6: Create repair parts
        self.stdout.write('\n[6/11] Creating repair parts...')
        self.create_repair_parts()
        
        # Step 7: Create pre-inspection reports (required for repairs and PMS)
        self.stdout.write('\n[7/11] Creating pre-inspection reports...')
        self.create_pre_inspections()
        
        # Step 8: Create repair records with parts (needs pre-inspections)
        self.stdout.write('\n[8/11] Creating repair records...')
        self.create_repairs()
        
        # Step 9: Create PMS records (needs pre-inspections)
        self.stdout.write('\n[9/11] Creating PMS records...')
        self.create_pms_records()
        
        # Step 10: Create post-inspection reports
        self.stdout.write('\n[10/11] Creating post-inspection reports...')
        self.create_post_inspections()
        
        # Step 11: Create notifications
        self.stdout.write('\n[11/11] Creating notifications...')
        self.create_notifications()
        
        # Summary
        self.print_summary()
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('ALL TEST DATA SUCCESSFULLY CREATED!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

    def create_users(self):
        """Create users with different permission sets"""
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@denr.gov.ph',
                'first_name': 'System',
                'last_name': 'Administrator',
                'status': 'active',
                'phone': '+63-900-000-0000',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'  [OK] Created admin user: admin (password: admin123)'))
        else:
            self.stdout.write(self.style.WARNING(f'  [-] Admin user already exists'))
            if not admin_user.check_password('admin123'):
                admin_user.set_password('admin123')
                admin_user.save()
        
        users_data = [
            {
                'username': 'fleet_manager',
                'email': 'fleet.manager@denr.gov.ph',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'status': 'active',
                'phone': '+63-912-345-6789',
                'permissions': {
                    'can_view_vehicles': True, 'can_add_vehicles': True,
                    'can_edit_vehicles': True, 'can_delete_vehicles': True,
                    'can_view_repairs': True, 'can_add_repairs': True,
                    'can_edit_repairs': True, 'can_delete_repairs': True,
                    'can_complete_repairs': True,
                    'can_view_pms': True, 'can_add_pms': True,
                    'can_edit_pms': True, 'can_delete_pms': True,
                    'can_complete_pms': True,
                    'can_view_inspections': True, 'can_add_inspections': True,
                    'can_edit_inspections': True, 'can_delete_inspections': True,
                    'can_approve_inspections': True,
                    'can_view_reports': True, 'can_view_operational_status': True,
                    'can_view_users': True,
                }
            },
            {
                'username': 'encoder',
                'email': 'encoder@denr.gov.ph',
                'first_name': 'Michael',
                'last_name': 'Brown',
                'status': 'active',
                'phone': '+63-923-456-7890',
                'permissions': {
                    'can_view_vehicles': True, 'can_add_vehicles': True,
                    'can_edit_vehicles': True,
                    'can_view_repairs': True, 'can_add_repairs': True,
                    'can_view_pms': True, 'can_add_pms': True,
                    'can_view_inspections': True, 'can_add_inspections': True,
                }
            },
            {
                'username': 'inspector',
                'email': 'inspector@denr.gov.ph',
                'first_name': 'Lisa',
                'last_name': 'Wilson',
                'status': 'active',
                'phone': '+63-934-567-8901',
                'permissions': {
                    'can_view_vehicles': True,
                    'can_view_repairs': True,
                    'can_view_pms': True,
                    'can_view_inspections': True, 'can_add_inspections': True,
                    'can_edit_inspections': True, 'can_approve_inspections': True,
                }
            },
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'status': user_data['status'],
                    'phone': user_data['phone'],
                }
            )
            
            if created:
                user.set_password('password123')
                for perm, value in user_data['permissions'].items():
                    setattr(user, perm, value)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created user: {user.username} (password: password123)'))
            else:
                self.stdout.write(self.style.WARNING(f'  [-] User already exists: {user.username}'))

    def create_divisions(self):
        """Create divisions"""
        divisions = [
            'Administrative Division',
            'Operations Division',
            'Technical Division',
            'Planning and Development Division',
            'Finance Division',
            'Legal Division',
            'Information Technology Division',
            'Human Resources Division',
            'Environmental Division',
            'Research and Development Division',
            'Environmental Management Division',
            'Forest Management Division',
            'Mining and Geosciences Division',
            'Biodiversity Management Division',
            'Climate Change Division',
            'Procurement Division',
            'Internal Audit Division'
        ]
        
        created = 0
        for div_name in divisions:
            division, new = Division.objects.get_or_create(
                name=div_name,
                defaults={'description': f'Description for {div_name}'}
            )
            if new:
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} divisions'))

    def create_drivers(self):
        """Create drivers"""
        drivers_data = [
            ('Juan Dela Cruz', 'D01-123456', '+63-945-678-9012', 'juan.delacruz@denr.gov.ph'),
            ('Maria Santos', 'D02-234567', '+63-956-789-0123', 'maria.santos@denr.gov.ph'),
            ('Pedro Garcia', 'D03-345678', '+63-967-890-1234', 'pedro.garcia@denr.gov.ph'),
            ('Ana Rodriguez', 'D04-456789', '+63-978-901-2345', 'ana.rodriguez@denr.gov.ph'),
            ('Carlos Lopez', 'D05-567890', '+63-989-012-3456', 'carlos.lopez@denr.gov.ph'),
            ('Roberto Martinez', 'D06-678901', '+63-990-123-4567', 'roberto.martinez@denr.gov.ph'),
            ('Elena Fernandez', 'D07-789012', '+63-901-234-5678', 'elena.fernandez@denr.gov.ph'),
            ('Antonio Cruz', 'D08-890123', '+63-912-345-6789', 'antonio.cruz@denr.gov.ph'),
            ('Isabella Torres', 'D09-901234', '+63-923-456-7890', 'isabella.torres@denr.gov.ph'),
            ('Fernando Ramos', 'D10-012345', '+63-934-567-8901', 'fernando.ramos@denr.gov.ph'),
        ]
        
        created = 0
        for name, license_num, phone, email in drivers_data:
            driver, new = Driver.objects.get_or_create(
                license_number=license_num,
                defaults={'name': name, 'phone': phone, 'email': email}
            )
            if new:
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} drivers'))

    def create_vehicles(self):
        """Create vehicles"""
        divisions = list(Division.objects.all())
        drivers = list(Driver.objects.all())
        admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        
        vehicles_data = [
            ('ABC-1234', 'Toyota', 'Vios', 2020, 'Sedan', 'Serviceable', 35000, 850000),
            ('DEF-5678', 'Honda', 'CR-V', 2019, 'SUV', 'Serviceable', 28000, 1450000),
            ('GHI-9012', 'Ford', 'Everest', 2021, 'SUV', 'Under Repair', 45000, 1250000),
            ('JKL-3456', 'Mitsubishi', 'Montero', 2018, 'SUV', 'Serviceable', 52000, 1350000),
            ('MNO-7890', 'Nissan', 'Navara', 2020, 'Pickup Truck', 'Serviceable', 38000, 1200000),
            ('PQR-2468', 'Isuzu', 'D-Max', 2019, 'Pickup Truck', 'Unserviceable', 60000, 1150000),
            ('STU-1357', 'Hyundai', 'Accent', 2021, 'Sedan', 'Serviceable', 25000, 750000),
            ('VWX-9753', 'Suzuki', 'Ertiga', 2020, 'Van', 'Serviceable', 40000, 950000),
            ('YZA-8642', 'Chevrolet', 'Trailblazer', 2019, 'SUV', 'Under Repair', 55000, 1300000),
            ('BCD-7531', 'Mazda', 'CX-5', 2021, 'SUV', 'Serviceable', 30000, 1400000),
            ('EFG-1111', 'Toyota', 'Hilux', 2019, 'Pickup Truck', 'Serviceable', 48000, 1200000),
            ('HIJ-2222', 'Toyota', 'Innova', 2020, 'Van', 'Serviceable', 42000, 1050000),
            ('KLM-3333', 'Honda', 'Civic', 2021, 'Sedan', 'Serviceable', 22000, 950000),
            ('NOP-4444', 'Nissan', 'Terra', 2020, 'SUV', 'Serviceable', 35000, 1350000),
            ('QRS-5555', 'Isuzu', 'Mu-X', 2019, 'SUV', 'Serviceable', 50000, 1280000),
        ]
        
        created = 0
        for plate, brand, model, year, vtype, status, mileage, cost in vehicles_data:
            vehicle, new = Vehicle.objects.get_or_create(
                plate_number=plate,
                defaults={
                    'brand': brand, 'model': model, 'year': year,
                    'vehicle_type': vtype, 'status': status,
                    'division': random.choice(divisions) if divisions else None,
                    'assigned_driver': random.choice(drivers) if drivers else None,
                    'date_acquired': datetime.now().date() - timedelta(days=random.randint(30, 1500)),
                    'current_mileage': mileage,
                    'acquisition_cost': Decimal(str(cost)),
                    'engine_number': f'ENG-{random.randint(100000, 999999)}',
                    'chassis_number': f'CHS-{random.randint(100000, 999999)}',
                    'color': random.choice(['White', 'Black', 'Silver', 'Blue', 'Red', 'Gray']),
                    'rfid_number': f'RFID-{random.randint(100000, 999999)}',
                    'rfid_type': random.choice(['Autosweep', 'Easytrip']) if random.random() > 0.3 else None,
                    'fleet_card_number': f'FC-{random.randint(100000, 999999)}',
                    'gas_station': random.choice(['Shell', 'Petron', 'Caltex', 'Total']),
                    'status_changed_at': timezone.now() - timedelta(days=random.randint(1, 90)),
                    'status_changed_by': admin_user,
                }
            )
            if new:
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} vehicles'))

    def create_repair_shops(self):
        """Create repair shops"""
        shops_data = [
            ('AutoCare Plus', '123 Main Street, Quezon City', '+63-2-1234-5678', 'info@autocareplus.com', 'Juan Dela Cruz'),
            ('Metro Motors Service Center', '456 EDSA, Mandaluyong City', '+63-2-2345-6789', 'service@metromotors.com', 'Maria Santos'),
            ('Fleet Maintenance Co.', '789 Ortigas Avenue, Pasig City', '+63-2-3456-7890', 'fleet@maintenance.com', 'Pedro Rodriguez'),
            ('Quick Fix Garage', '321 Taft Avenue, Manila City', '+63-2-4567-8901', 'quickfix@garage.com', 'Ana Garcia'),
            ('Professional Auto Repair', '654 Commonwealth Avenue, Quezon City', '+63-2-5678-9012', 'pro@autorepair.com', 'Carlos Mendoza'),
            ('Express Service Center', '987 Ayala Avenue, Makati City', '+63-2-6789-0123', 'express@service.com', 'Lisa Torres'),
            ('Reliable Motors', '147 Shaw Boulevard, Mandaluyong City', '+63-2-7890-1234', 'reliable@motors.com', 'Roberto Silva'),
            ('City Auto Works', '258 Timog Avenue, Quezon City', '+63-2-8901-2345', 'city@autoworks.com', 'Carmen Reyes'),
        ]
        
        created = 0
        for name, address, phone, email, contact in shops_data:
            shop, new = RepairShop.objects.get_or_create(
                name=name,
                defaults={
                    'address': address, 'phone': phone, 'email': email,
                    'contact_person': contact, 'is_active': True
                }
            )
            if new:
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} repair shops'))

    def create_repair_parts(self):
        """Create repair parts"""
        parts_data = [
            'Engine Oil', 'Oil Filter', 'Air Filter', 'Cabin Filter', 'Fuel Filter',
            'Spark Plugs', 'Water Pump', 'Radiator', 'Thermostat', 'Fan Belt',
            'Serpentine Belt', 'Timing Belt', 'Alternator', 'Starter Motor', 'Fuel Pump',
            'Transmission Fluid', 'Clutch Disc', 'Clutch Pressure Plate', 'Brake Pads',
            'Brake Rotors', 'Brake Calipers', 'Brake Fluid', 'Car Battery',
            'Headlights', 'Taillights', 'Turn Signals', 'Shock Absorbers',
            'Struts', 'Tires', 'Wheel Bearings', 'Muffler', 'Catalytic Converter',
            'A/C Compressor', 'A/C Refrigerant', 'Coolant/Antifreeze',
            'Windshield Wiper Blades', 'Side Mirrors', 'Windshield',
        ]
        
        created = 0
        for part_name in parts_data:
            part, new = RepairPart.objects.get_or_create(
                name=part_name,
                defaults={'description': f'Description for {part_name}', 'is_active': True}
            )
            if new:
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} repair parts'))

    def create_repairs(self):
        """Create repair records with parts"""
        vehicles = list(Vehicle.objects.all())
        repair_shops = list(RepairShop.objects.filter(is_active=True))
        repair_parts = list(RepairPart.objects.filter(is_active=True))
        # Get approved pre-inspections for repairs
        pre_inspections = list(PreInspectionReport.objects.filter(
            approved_by__isnull=False, report_type='repair'
        ))
        
        if not vehicles or not repair_parts:
            self.stdout.write(self.style.WARNING('  [-] Skipping repairs (missing vehicles or parts)'))
            return
        
        if not pre_inspections:
            self.stdout.write(self.style.WARNING('  [-] Skipping repairs (no approved pre-inspections for repairs)'))
            return
        
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
        ]
        
        common_parts = {
            'Engine Oil': {'qty': Decimal('4'), 'unit': 'liter', 'cost': Decimal('1500.00')},
            'Oil Filter': {'qty': Decimal('1'), 'unit': 'pcs', 'cost': Decimal('450.00')},
            'Air Filter': {'qty': Decimal('1'), 'unit': 'pcs', 'cost': Decimal('850.00')},
            'Brake Pads': {'qty': Decimal('4'), 'unit': 'pcs', 'cost': Decimal('3500.00')},
            'Brake Rotors': {'qty': Decimal('2'), 'unit': 'pcs', 'cost': Decimal('4500.00')},
            'Spark Plugs': {'qty': Decimal('4'), 'unit': 'pcs', 'cost': Decimal('1200.00')},
            'Coolant/Antifreeze': {'qty': Decimal('6'), 'unit': 'liter', 'cost': Decimal('1800.00')},
            'Car Battery': {'qty': Decimal('1'), 'unit': 'pcs', 'cost': Decimal('8500.00')},
        }
        
        created = 0
        # Limit to number of available pre-inspections
        for i in range(min(15, len(pre_inspections))):
            # Get a pre-inspection (reuse if needed)
            pre_inspection = pre_inspections[i % len(pre_inspections)]
            vehicle = pre_inspection.vehicle
            days_ago = random.randint(1, 365)
            repair_date = datetime.now().date() - timedelta(days=days_ago)
            # Only create as Ongoing - completed repairs require post-inspections
            status = 'Ongoing'
            
            repair = Repair.objects.create(
                vehicle=vehicle,
                date_of_repair=repair_date,
                description=random.choice(descriptions),
                status=status,
                repair_shop=random.choice(repair_shops) if repair_shops else None,
                technician=random.choice(['Juan Dela Cruz', 'Maria Santos', 'Pedro Garcia']),
                cost=Decimal('0'),
                labor_cost=Decimal(str(random.randint(500, 3000))),
                pre_inspection=pre_inspection  # Link to pre-inspection
            )
            
            # Add parts
            num_parts = random.randint(1, 3)
            selected_part_names = random.sample(list(common_parts.keys()), min(num_parts, len(common_parts)))
            total_cost = Decimal('0')
            
            for part_name in selected_part_names:
                part_obj = next((p for p in repair_parts if p.name == part_name), None)
                if part_obj:
                    part_data = common_parts[part_name]
                    RepairPartItem.objects.create(
                        repair=repair,
                        part=part_obj,
                        quantity=part_data['qty'],
                        unit=part_data['unit'],
                        cost=part_data['cost'],
                    )
                    total_cost += part_data['cost']
            
            repair.cost = total_cost
            repair.save()
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} repair records'))

    def create_pms_records(self):
        """Create PMS records"""
        vehicles = list(Vehicle.objects.all())
        # Get approved pre-inspections for PMS
        pre_inspections = list(PreInspectionReport.objects.filter(
            approved_by__isnull=False, report_type='pms'
        ))
        
        if not vehicles:
            self.stdout.write(self.style.WARNING('  [-] Skipping PMS (no vehicles)'))
            return
        
        if not pre_inspections:
            self.stdout.write(self.style.WARNING('  [-] Skipping PMS (no approved pre-inspections for PMS)'))
            return
        
        providers = [
            'AutoCare Service Center', 'Quick Fix Garage', 'Professional Auto Repair',
            'Reliable Motors', 'Express Service Station', 'Precision Auto Works',
        ]
        
        created = 0
        # Limit to number of available pre-inspections
        for i in range(min(20, len(pre_inspections))):
            # Get a pre-inspection (reuse if needed)
            pre_inspection = pre_inspections[i % len(pre_inspections)]
            vehicle = pre_inspection.vehicle
            base_date = datetime.now().date() - timedelta(days=random.randint(30, 365))
            # Only create as non-completed - completed PMS requires post-inspections
            completed_date = None
            cost = None
            if base_date < datetime.now().date():
                status = 'Overdue'
            else:
                status = random.choice(['Scheduled', 'In Progress'])
            
            PMS.objects.create(
                vehicle=vehicle,
                service_type='General Inspection',
                scheduled_date=base_date,
                completed_date=completed_date,
                mileage_at_service=max(0, (vehicle.current_mileage or 0) - random.randint(1000, 5000)),
                next_service_mileage=(vehicle.current_mileage or 0) + random.randint(5000, 15000),
                cost=cost,
                provider=random.choice(providers),
                technician=random.choice(['Juan Dela Cruz', 'Pedro Santos', 'Maria Garcia']),
                description='Routine general inspection including engine, brakes, lights, and fluid levels.',
                status=status,
                pre_inspection=pre_inspection  # Link to pre-inspection
            )
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} PMS records'))

    def create_pre_inspections(self):
        """Create pre-inspection reports"""
        vehicles = list(Vehicle.objects.all())
        users = list(User.objects.all())
        
        if not vehicles or not users:
            self.stdout.write(self.style.WARNING('  [-] Skipping pre-inspections (missing data)'))
            return
        
        created = 0
        selected_vehicles = random.sample(vehicles, min(20, len(vehicles)))
        
        # Create mix of repair and PMS pre-inspections (about 50/50 split)
        for idx, vehicle in enumerate(selected_vehicles):
            # First 10 are repairs, next 10 are PMS (if we have 20)
            if idx < min(10, len(selected_vehicles)):
                report_type = 'repair'
            else:
                report_type = 'pms'
            
            pre_inspection = PreInspectionReport.objects.create(
                vehicle=vehicle,
                report_type=report_type,
                inspected_by=random.choice(users),
                engine_condition=random.choice(['excellent', 'good', 'fair', 'poor']),
                transmission_condition=random.choice(['excellent', 'good', 'fair']),
                brakes_condition=random.choice(['excellent', 'good', 'fair']),
                suspension_condition=random.choice(['excellent', 'good', 'fair']),
                electrical_condition=random.choice(['excellent', 'good', 'fair']),
                body_condition=random.choice(['excellent', 'good', 'fair']),
                tires_condition=random.choice(['excellent', 'good', 'fair']),
                lights_condition=random.choice(['excellent', 'good', 'fair']),
                current_mileage=(vehicle.current_mileage or 0) + random.randint(-1000, 1000),
                fuel_level=random.choice(['full', 'three_quarters', 'half', 'quarter']),
                issues_found=f'Issues found during pre-inspection for {vehicle.plate_number}',
                safety_concerns='No major safety concerns identified.',
                recommended_actions=f'Recommended actions before {report_type}',
                approved_by=random.choice(users),
                approval_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                approval_notes=f'Pre-inspection approved for {report_type} work'
            )
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} pre-inspection reports'))

    def create_post_inspections(self):
        """Create post-inspection reports"""
        pre_inspections = list(PreInspectionReport.objects.filter(approved_by__isnull=False))
        users = list(User.objects.all())
        
        if not pre_inspections or not users:
            self.stdout.write(self.style.WARNING('  [-] Skipping post-inspections (missing pre-inspections)'))
            return
        
        created = 0
        for pre_inspection in pre_inspections[:8]:  # Create for first 8 approved pre-inspections
            post_inspection = PostInspectionReport.objects.create(
                vehicle=pre_inspection.vehicle,
                report_type=pre_inspection.report_type,
                inspected_by=random.choice(users),
                pre_inspection=pre_inspection,
                work_completed_satisfactorily=True,
                quality_of_work=random.choice(['excellent', 'good', 'satisfactory']),
                timeliness=random.choice(['excellent', 'good', 'satisfactory']),
                cleanliness=random.choice(['excellent', 'good', 'satisfactory']),
                engine_condition=random.choice(['excellent', 'good']),
                transmission_condition=random.choice(['excellent', 'good']),
                brakes_condition=random.choice(['excellent', 'good']),
                suspension_condition=random.choice(['excellent', 'good']),
                electrical_condition=random.choice(['excellent', 'good']),
                body_condition=random.choice(['excellent', 'good']),
                tires_condition=random.choice(['excellent', 'good']),
                lights_condition=random.choice(['excellent', 'good']),
                test_drive_performed=True,
                test_drive_distance=random.randint(5, 20),
                test_drive_notes='Test drive completed successfully.',
                remaining_issues='No remaining issues identified.',
                future_recommendations='Monitor condition regularly.',
                approved_by=random.choice(users),
                approval_date=timezone.now() - timedelta(days=random.randint(0, 5)),
                approval_notes='Post-inspection approved.'
            )
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} post-inspection reports'))

    def create_notifications(self):
        """Create notifications"""
        users = list(User.objects.all())
        
        if not users:
            self.stdout.write(self.style.WARNING('  [-] Skipping notifications (no users)'))
            return
        
        notifications_data = [
            ('PMS Reminder', 'Vehicle PMS is due for maintenance', 'pms_reminder'),
            ('Repair Completed', 'Repair has been completed', 'repair_completed'),
            ('Vehicle Status Change', 'Vehicle status changed to Under Repair', 'vehicle_status'),
            ('Overdue PMS', 'Vehicle PMS is overdue', 'pms_overdue'),
            ('General Notification', 'System maintenance scheduled', 'general'),
        ]
        
        created = 0
        for title, message, ntype in notifications_data * 3:  # Create 15 notifications
            Notification.objects.create(
                user=random.choice(users),
                notification_type=ntype,
                title=title,
                message=message,
                priority=random.choice(['low', 'medium', 'high']),
                is_read=random.choice([True, False]),
            )
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} notifications'))

    def print_summary(self):
        """Print database summary"""
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('DATABASE SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        self.stdout.write(f'\n  Users: {User.objects.count()}')
        self.stdout.write(f'  Divisions: {Division.objects.count()}')
        self.stdout.write(f'  Drivers: {Driver.objects.count()}')
        self.stdout.write(f'  Vehicles: {Vehicle.objects.count()}')
        self.stdout.write(f'  Repair Shops: {RepairShop.objects.count()}')
        self.stdout.write(f'  Repair Parts: {RepairPart.objects.count()}')
        self.stdout.write(f'  Repairs: {Repair.objects.count()}')
        self.stdout.write(f'  Repair Part Items: {RepairPartItem.objects.count()}')
        self.stdout.write(f'  PMS Records: {PMS.objects.count()}')
        self.stdout.write(f'  Pre-Inspections: {PreInspectionReport.objects.count()}')
        self.stdout.write(f'  Post-Inspections: {PostInspectionReport.objects.count()}')
        self.stdout.write(f'  Notifications: {Notification.objects.count()}')

