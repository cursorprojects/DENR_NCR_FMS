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
from dateutil.relativedelta import relativedelta
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
        self.stdout.write(self.style.SUCCESS('FLEET MANAGEMENT SYSTEM - COMPREHENSIVE TEST DATA CREATION'))
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
        
        # Step 4: Create vehicles with ALL statuses
        self.stdout.write('\n[4/11] Creating vehicles (all statuses)...')
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
        
        # Step 8: Create post-inspection reports (needed before completed repairs/PMS)
        self.stdout.write('\n[8/11] Creating post-inspection reports...')
        self.create_post_inspections()
        
        # Step 9: Create PMS records FIRST (Scheduled/Overdue for Serviceable vehicles) - BEFORE repairs/PMS that change status
        self.stdout.write('\n[9/11] Creating PMS records (all statuses)...')
        self.create_pms_records()
        
        # Step 10: Create repair records with ALL statuses and all fields (AFTER PMS so some vehicles can stay Serviceable)
        self.stdout.write('\n[10/11] Creating repair records (all statuses)...')
        self.create_repairs()
        
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
            {
                'username': 'viewer',
                'email': 'viewer@denr.gov.ph',
                'first_name': 'John',
                'last_name': 'Doe',
                'status': 'active',
                'phone': '+63-945-678-9012',
                'permissions': {
                    'can_view_vehicles': True,
                    'can_view_repairs': True,
                    'can_view_pms': True,
                    'can_view_inspections': True,
                }
            },
            {
                'username': 'inactive_user',
                'email': 'inactive@denr.gov.ph',
                'first_name': 'Inactive',
                'last_name': 'User',
                'status': 'inactive',
                'phone': '+63-956-789-0123',
                'permissions': {}
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
        """Create vehicles with ALL statuses and ALL fields populated"""
        divisions = list(Division.objects.all())
        drivers = list(Driver.objects.all())
        admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        
        # Vehicle data with variety of statuses
        # Adding more Serviceable vehicles for better sample data
        vehicles_data = [
            # Serviceable vehicles - more entries for better coverage
            ('ABC-1234', 'Toyota', 'Vios', 2020, 'Sedan', 'Serviceable', 35000, 850000),
            ('DEF-5678', 'Honda', 'CR-V', 2019, 'SUV', 'Serviceable', 28000, 1450000),
            ('GHI-9012', 'Mitsubishi', 'Montero', 2018, 'SUV', 'Serviceable', 52000, 1350000),
            ('JKL-3456', 'Nissan', 'Navara', 2020, 'Pickup Truck', 'Serviceable', 38000, 1200000),
            ('MNO-7890', 'Hyundai', 'Accent', 2021, 'Sedan', 'Serviceable', 25000, 750000),
            ('PQR-2468', 'Suzuki', 'Ertiga', 2020, 'Van', 'Serviceable', 40000, 950000),
            ('STU-1357', 'Mazda', 'CX-5', 2021, 'SUV', 'Serviceable', 30000, 1400000),
            ('VWX-9753', 'Toyota', 'Hilux', 2019, 'Pickup Truck', 'Serviceable', 48000, 1200000),
            ('YZA-8642', 'Toyota', 'Innova', 2020, 'Van', 'Serviceable', 42000, 1050000),
            ('BCD-7531', 'Honda', 'Civic', 2021, 'Sedan', 'Serviceable', 22000, 950000),
            ('EFG-1111', 'Nissan', 'Terra', 2020, 'SUV', 'Serviceable', 35000, 1350000),
            ('HIJ-2222', 'Isuzu', 'Mu-X', 2019, 'SUV', 'Serviceable', 50000, 1280000),
            ('KLM-3333', 'Toyota', 'Fortuner', 2021, 'SUV', 'Serviceable', 33000, 1450000),
            ('NOP-4444', 'Honda', 'BR-V', 2020, 'SUV', 'Serviceable', 37000, 1300000),
            ('QRS-5555', 'Mitsubishi', 'Strada', 2019, 'Pickup Truck', 'Serviceable', 55000, 1250000),
            ('TUV-6666', 'Ford', 'Ranger', 2021, 'Pickup Truck', 'Serviceable', 29000, 1400000),
            ('WXY-7777', 'Chevrolet', 'Colorado', 2020, 'Pickup Truck', 'Serviceable', 41000, 1280000),
            ('ZAB-8888', 'Nissan', 'Almera', 2021, 'Sedan', 'Serviceable', 27000, 850000),
            ('CDE-9999', 'Suzuki', 'APV', 2020, 'Van', 'Serviceable', 46000, 900000),
            ('FGH-0000', 'Toyota', 'Avanza', 2019, 'Van', 'Serviceable', 52000, 950000),
            
            # Under Repair vehicles
            ('REP-0001', 'Ford', 'Everest', 2021, 'SUV', 'Under Repair', 45000, 1250000),
            ('REP-0002', 'Chevrolet', 'Trailblazer', 2019, 'SUV', 'Under Repair', 55000, 1300000),
            ('REP-0003', 'Toyota', 'Camry', 2020, 'Sedan', 'Under Repair', 32000, 1450000),
            ('REP-0004', 'Honda', 'Accord', 2021, 'Sedan', 'Under Repair', 29000, 1400000),
            
            # Unserviceable vehicles
            ('UNS-0001', 'Isuzu', 'D-Max', 2019, 'Pickup Truck', 'Unserviceable', 60000, 1150000),
            ('UNS-0002', 'Mitsubishi', 'L300', 2018, 'Van', 'Unserviceable', 70000, 800000),
            ('UNS-0003', 'Nissan', 'Urvan', 2017, 'Van', 'Unserviceable', 80000, 950000),
        ]
        
        colors = ['White', 'Black', 'Silver', 'Blue', 'Red', 'Gray', 'Green', 'Brown', 'Beige']
        rfid_types = ['Autosweep', 'Easytrip']
        gas_stations = ['Shell', 'Petron', 'Caltex', 'Total', 'Unioil', 'Seaoil']
        status_reasons = [
            'Regular operational status',
            'Currently in use',
            'Available for assignment',
            'Under maintenance',
            'Waiting for parts',
            'Major repair in progress',
            'Out of service - awaiting disposal',
            'Non-operational - needs replacement',
        ]
        
        created = 0
        for plate, brand, model, year, vtype, status, mileage, cost in vehicles_data:
            vehicle, new = Vehicle.objects.get_or_create(
                plate_number=plate,
                defaults={
                    'brand': brand, 
                    'model': model, 
                    'year': year,
                    'vehicle_type': vtype, 
                    'status': status,
                    'division': random.choice(divisions) if divisions else None,
                    'assigned_driver': random.choice(drivers) if drivers else None,
                    'date_acquired': datetime.now().date() - timedelta(days=random.randint(30, 1500)),
                    'current_mileage': mileage,
                    'acquisition_cost': Decimal(str(cost)),
                    'engine_number': f'ENG-{random.randint(100000, 999999)}',
                    'chassis_number': f'CHS-{random.randint(100000, 999999)}',
                    'color': random.choice(colors),
                    'rfid_number': f'RFID-{random.randint(100000, 999999)}' if random.random() > 0.2 else '',
                    'rfid_type': random.choice(rfid_types) if random.random() > 0.3 else None,
                    'fleet_card_number': f'FC-{random.randint(100000, 999999)}' if random.random() > 0.2 else '',
                    'gas_station': random.choice(gas_stations) if random.random() > 0.2 else '',
                    'notes': f'Vehicle notes for {plate}. Status: {status}.',
                    'status_changed_at': timezone.now() - timedelta(days=random.randint(1, 90)),
                    'status_changed_by': admin_user,
                    'status_change_reason': random.choice(status_reasons),
                }
            )
            if new:
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} vehicles (Serviceable: {Vehicle.objects.filter(status="Serviceable").count()}, Under Repair: {Vehicle.objects.filter(status="Under Repair").count()}, Unserviceable: {Vehicle.objects.filter(status="Unserviceable").count()})'))

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
                    'address': address, 
                    'phone': phone, 
                    'email': email,
                    'contact_person': contact, 
                    'is_active': random.choice([True, True, True, False])  # Mostly active
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
                defaults={
                    'description': f'Description for {part_name}. Quality assured replacement part.',
                    'is_active': random.choice([True, True, True, False])  # Mostly active
                }
            )
            if new:
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} repair parts'))

    def create_pre_inspections(self):
        """Create pre-inspection reports - mix of approved and unapproved"""
        vehicles = list(Vehicle.objects.all())
        users = list(User.objects.all())
        
        if not vehicles or not users:
            self.stdout.write(self.style.WARNING('  [-] Skipping pre-inspections (missing data)'))
            return
        
        conditions = ['excellent', 'good', 'fair', 'poor', 'critical']
        fuel_levels = ['full', 'three_quarters', 'half', 'quarter', 'empty']
        
        created_repair = 0
        created_pms = 0
        created_approved = 0
        created_unapproved = 0
        
        # Create more pre-inspections to cover all scenarios
        num_pre_inspections = min(40, len(vehicles) * 2)
        selected_vehicles = random.sample(vehicles, min(num_pre_inspections // 2, len(vehicles)))
        
        for idx, vehicle in enumerate(selected_vehicles):
            # Alternate between repair and PMS
            if idx % 2 == 0:
                report_type = 'repair'
                created_repair += 1
            else:
                report_type = 'pms'
                created_pms += 1
            
            # Mix of approved and unapproved (70% approved)
            should_approve = random.random() < 0.7
            
            pre_inspection = PreInspectionReport.objects.create(
                vehicle=vehicle,
                report_type=report_type,
                inspected_by=random.choice(users),
                engine_condition=random.choice(conditions),
                transmission_condition=random.choice(conditions),
                brakes_condition=random.choice(conditions),
                suspension_condition=random.choice(conditions),
                electrical_condition=random.choice(conditions),
                body_condition=random.choice(conditions),
                tires_condition=random.choice(conditions),
                lights_condition=random.choice(conditions),
                current_mileage=(vehicle.current_mileage or 0) + random.randint(-1000, 1000),
                fuel_level=random.choice(fuel_levels),
                issues_found=f'Issues found during pre-inspection for {vehicle.plate_number}. Some components may need attention.',
                safety_concerns='No major safety concerns identified.' if random.random() > 0.3 else 'Minor safety concerns noted.',
                recommended_actions=f'Recommended actions before {report_type} work. Follow standard procedures.',
                photos=[],  # Empty photos array
                approved_by=random.choice(users) if should_approve else None,
                approval_date=timezone.now() - timedelta(days=random.randint(1, 30)) if should_approve else None,
                approval_notes=f'Pre-inspection approved for {report_type} work' if should_approve else ''
            )
            
            if should_approve:
                created_approved += 1
            else:
                created_unapproved += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created_repair + created_pms} pre-inspection reports (Repair: {created_repair}, PMS: {created_pms}, Approved: {created_approved}, Unapproved: {created_unapproved})'))

    def create_repairs(self):
        """Create repair records with ALL statuses and ALL fields populated"""
        vehicles = list(Vehicle.objects.all())
        repair_shops = list(RepairShop.objects.filter(is_active=True))
        repair_parts = list(RepairPart.objects.filter(is_active=True))
        # Get approved pre-inspections for repairs that are NOT already used
        # Get pre-inspections already used in database
        used_pre_inspection_ids = set()
        used_pre_inspection_ids.update(
            Repair.objects.exclude(pre_inspection__isnull=True)
                         .values_list('pre_inspection_id', flat=True)
        )
        used_pre_inspection_ids.update(
            PMS.objects.exclude(pre_inspection__isnull=True)
                      .values_list('pre_inspection_id', flat=True)
        )
        
        # Get available pre-inspections (not used)
        pre_inspections = list(PreInspectionReport.objects.filter(
            approved_by__isnull=False, report_type='repair'
        ).exclude(id__in=used_pre_inspection_ids))
        users = list(User.objects.all())
        
        if not vehicles or not repair_parts:
            self.stdout.write(self.style.WARNING('  [-] Skipping repairs (missing vehicles or parts)'))
            return
        
        if not pre_inspections:
            self.stdout.write(self.style.WARNING('  [-] Skipping repairs (no available approved pre-inspections for repairs)'))
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
            'Engine overhaul and component replacement',
            'Cooling system repair - radiator and hose replacement',
            'Electrical system diagnosis and repair',
            'Body repair and paint work',
            'Exhaust system repair and muffler replacement',
        ]
        
        technicians = [
            'Juan Dela Cruz', 'Maria Santos', 'Pedro Garcia', 
            'Roberto Martinez', 'Carlos Mendoza', 'Lisa Torres'
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
            'Water Pump': {'qty': Decimal('1'), 'unit': 'pcs', 'cost': Decimal('6500.00')},
            'Alternator': {'qty': Decimal('1'), 'unit': 'pcs', 'cost': Decimal('12000.00')},
        }
        
        # Get post-inspections for completed repairs that haven't been used yet
        used_post_inspection_ids = set()
        used_post_inspection_ids.update(
            Repair.objects.exclude(post_inspection__isnull=True)
                         .values_list('post_inspection_id', flat=True)
        )
        
        post_inspections = list(PostInspectionReport.objects.filter(
            approved_by__isnull=False, report_type='repair'
        ).exclude(id__in=used_post_inspection_ids))
        
        created_ongoing = 0
        created_completed = 0
        
        # Track pre-inspections used in this run
        used_pre_inspection_ids_in_run = set()
        
        # Create Ongoing repairs (more common) - ensure vehicles are set to "Under Repair" status
        num_ongoing = min(15, len(pre_inspections))
        for i in range(num_ongoing):
            # Find an unused pre-inspection
            available_pre_inspections = [pi for pi in pre_inspections if pi.id not in used_pre_inspection_ids_in_run]
            if not available_pre_inspections:
                break
                
            pre_inspection = random.choice(available_pre_inspections)
            used_pre_inspection_ids_in_run.add(pre_inspection.id)
            vehicle = pre_inspection.vehicle
            days_ago = random.randint(1, 90)
            repair_date = datetime.now().date() - timedelta(days=days_ago)
            
            repair = Repair.objects.create(
                vehicle=vehicle,
                date_of_repair=repair_date,
                description=random.choice(descriptions),
                status='Ongoing',
                repair_shop=random.choice(repair_shops) if repair_shops else None,
                technician=random.choice(technicians),
                cost=Decimal('0'),
                labor_cost=Decimal(str(random.randint(500, 3000))),
                pre_inspection=pre_inspection,
                post_inspection=None
            )
            
            # Add parts
            num_parts = random.randint(1, 4)
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
            
            # Update vehicle status to "Under Repair" if it's Serviceable
            # (This follows the correct logic - repairs automatically change vehicle status)
            if vehicle.status == 'Serviceable':
                vehicle.update_status('Under Repair', user=users[0] if users else None, reason=f'Ongoing repair: {repair.description[:50]}', auto_update=True)
            
            created_ongoing += 1
        
        # Create Completed repairs (need post-inspections)
        # Use only repair-type post-inspections whose pre-inspections haven't been used in this run
        repair_post_inspections = [
            pi for pi in post_inspections 
            if pi.report_type == 'repair' and pi.pre_inspection.id not in used_pre_inspection_ids_in_run
        ]
        num_completed = min(8, len(repair_post_inspections))
        for i in range(num_completed):
            # Find an available post-inspection with unused pre-inspection
            available_post_inspections = [
                pi for pi in repair_post_inspections 
                if pi.pre_inspection.id not in used_pre_inspection_ids_in_run
            ]
            if not available_post_inspections:
                break
                
            post_inspection = random.choice(available_post_inspections)
            pre_inspection = post_inspection.pre_inspection
            used_pre_inspection_ids_in_run.add(pre_inspection.id)
            vehicle = post_inspection.vehicle
                
            days_ago = random.randint(10, 180)
            repair_date = datetime.now().date() - timedelta(days=days_ago)
            
            repair = Repair.objects.create(
                vehicle=vehicle,
                date_of_repair=repair_date,
                description=random.choice(descriptions),
                status='Completed',
                repair_shop=random.choice(repair_shops) if repair_shops else None,
                technician=random.choice(technicians),
                cost=Decimal('0'),
                labor_cost=Decimal(str(random.randint(1000, 5000))),
                pre_inspection=pre_inspection,
                post_inspection=post_inspection
            )
            
            # Add parts
            num_parts = random.randint(2, 5)
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
            created_completed += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created_ongoing + created_completed} repair records (Ongoing: {created_ongoing}, Completed: {created_completed})'))

    def create_pms_records(self):
        """Create PMS records with ALL statuses and ALL fields populated"""
        vehicles = list(Vehicle.objects.all())
        # Get approved pre-inspections for PMS that are NOT already used
        # Get pre-inspections already used in database
        used_pre_inspection_ids = set()
        used_pre_inspection_ids.update(
            Repair.objects.exclude(pre_inspection__isnull=True)
                         .values_list('pre_inspection_id', flat=True)
        )
        used_pre_inspection_ids.update(
            PMS.objects.exclude(pre_inspection__isnull=True)
                      .values_list('pre_inspection_id', flat=True)
        )
        
        # Get available pre-inspections (not used)
        pre_inspections = list(PreInspectionReport.objects.filter(
            approved_by__isnull=False, report_type='pms'
        ).exclude(id__in=used_pre_inspection_ids))
        users = list(User.objects.all())
        
        if not vehicles:
            self.stdout.write(self.style.WARNING('  [-] Skipping PMS (no vehicles)'))
            return
        
        if not pre_inspections:
            self.stdout.write(self.style.WARNING('  [-] Skipping PMS (no available approved pre-inspections for PMS)'))
            return
        
        # CRITICAL: Get fresh list of Serviceable vehicles at the start
        # We'll create Scheduled/Overdue PMS for these FIRST, before creating In Progress PMS
        serviceable_vehicles_fresh = list(Vehicle.objects.filter(status='Serviceable'))
        
        providers = [
            'AutoCare Service Center', 'Quick Fix Garage', 'Professional Auto Repair',
            'Reliable Motors', 'Express Service Station', 'Precision Auto Works',
        ]
        
        technicians = [
            'Juan Dela Cruz', 'Pedro Santos', 'Maria Garcia',
            'Roberto Martinez', 'Carlos Mendoza'
        ]
        
        descriptions = [
            'Routine general inspection including engine, brakes, lights, and fluid levels.',
            'Comprehensive PMS covering all major systems and components.',
            'Scheduled preventive maintenance service as per manufacturer recommendations.',
            'Full service including oil change, filter replacement, and system checks.',
            'Standard maintenance procedure with detailed inspection report.',
        ]
        
        notes_options = [
            'Regular scheduled maintenance',
            'No issues found during inspection',
            'Minor adjustments made',
            'All systems operating normally',
        ]
        
        # Get post-inspections for completed PMS that haven't been used yet
        used_post_inspection_ids = set()
        used_post_inspection_ids.update(
            PMS.objects.exclude(post_inspection__isnull=True)
                      .values_list('post_inspection_id', flat=True)
        )
        
        post_inspections = list(PostInspectionReport.objects.filter(
            approved_by__isnull=False, report_type='pms'
        ).exclude(id__in=used_post_inspection_ids))
        
        # Keep track of pre-inspections we use in this run
        used_pre_inspection_ids_in_run = set()
        
        today = datetime.now().date()
        created_scheduled = 0
        created_in_progress = 0
        created_completed = 0
        created_overdue = 0
        created_cancelled = 0
        
        # Create Scheduled PMS (future dates within 1 month) - these will show in "Near PMS"
        # IMPORTANT: Use the fresh list of Serviceable vehicles we got at the start
        # Filter pre-inspections to only those for Serviceable vehicles
        serviceable_vehicle_ids = [v.id for v in serviceable_vehicles_fresh]
        serviceable_pre_inspections = [
            pi for pi in pre_inspections 
            if pi.vehicle.id in serviceable_vehicle_ids
        ]
        
        # Create more to ensure good coverage for dashboard display
        num_scheduled = min(20, len(serviceable_pre_inspections))
        for i in range(num_scheduled):
            # Find an unused pre-inspection for Serviceable vehicles only
            available_pre_inspections = [pi for pi in serviceable_pre_inspections if pi.id not in used_pre_inspection_ids_in_run]
            if not available_pre_inspections:
                break
                
            pre_inspection = random.choice(available_pre_inspections)
            used_pre_inspection_ids_in_run.add(pre_inspection.id)
            vehicle = pre_inspection.vehicle
            
            # Double-check vehicle is still Serviceable (it might have been changed during this run)
            vehicle.refresh_from_db()
            if vehicle.status != 'Serviceable':
                continue  # Skip if vehicle is no longer Serviceable
            
            # Distribute dates to show various urgency levels on dashboard
            # Some today/tomorrow for immediate visibility, some soon, some later
            if i < 3:
                days_ahead = 0  # Today - will show "PMS scheduled today"
            elif i < 6:
                days_ahead = 1  # Tomorrow - will show "PMS scheduled tomorrow"
            elif i < 10:
                days_ahead = random.randint(2, 7)  # Within 1 week - urgent
            elif i < 15:
                days_ahead = random.randint(8, 14)  # 1-2 weeks
            else:
                days_ahead = random.randint(15, 30)  # 2-4 weeks
            scheduled_date = today + timedelta(days=days_ahead)
            
            PMS.objects.create(
                vehicle=vehicle,
                service_type='General Inspection',
                scheduled_date=scheduled_date,
                completed_date=None,
                mileage_at_service=(vehicle.current_mileage or 0) + random.randint(-500, 500),
                next_service_mileage=(vehicle.current_mileage or 0) + random.randint(5000, 15000),
                cost=None,
                provider=random.choice(providers),
                technician='',
                description=random.choice(descriptions),
                notes=random.choice(notes_options),
                status='Scheduled',
                pre_inspection=pre_inspection,
                post_inspection=None,
                repair=None
            )
            created_scheduled += 1
        
        # Create In Progress PMS (ongoing PMS) - ensure vehicles are set to "Under Repair" if Serviceable
        # Use remaining pre-inspections (not necessarily Serviceable)
        remaining_pre_inspections = [pi for pi in pre_inspections if pi.id not in used_pre_inspection_ids_in_run]
        # Create more ongoing PMS for better sample data
        num_in_progress = min(10, len(remaining_pre_inspections))
        for i in range(num_in_progress):
            # Find an unused pre-inspection
            available_pre_inspections = [pi for pi in remaining_pre_inspections if pi.id not in used_pre_inspection_ids_in_run]
            if not available_pre_inspections:
                break
                
            pre_inspection = random.choice(available_pre_inspections)
            used_pre_inspection_ids_in_run.add(pre_inspection.id)
            vehicle = pre_inspection.vehicle
            scheduled_date = today - timedelta(days=random.randint(1, 7))
            
            pms = PMS.objects.create(
                vehicle=vehicle,
                service_type='General Inspection',
                scheduled_date=scheduled_date,
                completed_date=None,
                mileage_at_service=(vehicle.current_mileage or 0) - random.randint(100, 500),
                next_service_mileage=(vehicle.current_mileage or 0) + random.randint(5000, 15000),
                cost=Decimal(str(random.randint(2000, 8000))),
                provider=random.choice(providers),
                technician=random.choice(technicians),
                description=random.choice(descriptions),
                notes='PMS currently in progress',
                status='In Progress',
                pre_inspection=pre_inspection,
                post_inspection=None,
                repair=None
            )
            
            # Update vehicle status to "Under Repair" if it's Serviceable
            # (This follows the correct logic - PMS In Progress automatically changes vehicle status)
            if vehicle.status == 'Serviceable':
                vehicle.update_status('Under Repair', user=users[0] if users else None, reason=f'PMS in progress: {pms.service_type}', auto_update=True)
            
            created_in_progress += 1
        
        # Create Overdue PMS (past scheduled date, not completed) - these will also show in "Near PMS"
        # IMPORTANT: Filter to only use Serviceable vehicles that are STILL Serviceable
        # (Some vehicles may have been changed to Under Repair by ongoing repairs/PMS, so re-check)
        serviceable_vehicles_list = list(Vehicle.objects.filter(status='Serviceable'))
        serviceable_pre_inspections_for_overdue = [
            pi for pi in serviceable_pre_inspections 
            if pi.vehicle.id in [v.id for v in serviceable_vehicles_list] and pi.id not in used_pre_inspection_ids_in_run
        ]
        
        for i in range(min(10, len(serviceable_pre_inspections_for_overdue))):
            # Find an unused pre-inspection for Serviceable vehicles only
            available_pre_inspections = [pi for pi in serviceable_pre_inspections_for_overdue if pi.id not in used_pre_inspection_ids_in_run]
            if not available_pre_inspections:
                break
                
            pre_inspection = random.choice(available_pre_inspections)
            used_pre_inspection_ids_in_run.add(pre_inspection.id)
            vehicle = pre_inspection.vehicle
            
            # Double-check vehicle is still Serviceable (it might have been changed during this run)
            vehicle.refresh_from_db()
            if vehicle.status != 'Serviceable':
                continue  # Skip if vehicle is no longer Serviceable
            
            # Vary overdue days: some recently overdue, some longer overdue
            if i < 5:
                days_overdue = random.randint(1, 7)  # Recently overdue (1-7 days)
            else:
                days_overdue = random.randint(8, 30)  # Longer overdue (8-30 days)
            scheduled_date = today - timedelta(days=days_overdue)
            
            PMS.objects.create(
                vehicle=vehicle,
                service_type='General Inspection',
                scheduled_date=scheduled_date,
                completed_date=None,
                mileage_at_service=(vehicle.current_mileage or 0) + random.randint(-500, 500),
                next_service_mileage=(vehicle.current_mileage or 0) + random.randint(5000, 15000),
                cost=None,
                provider=random.choice(providers),
                technician='',
                description=random.choice(descriptions),
                notes='PMS is overdue and needs rescheduling',
                status='Overdue',
                pre_inspection=pre_inspection,
                post_inspection=None,
                repair=None
            )
            created_overdue += 1
        
        # Create Cancelled PMS (can be any vehicle status)
        # Use remaining pre-inspections
        remaining_pre_inspections_for_cancel = [pi for pi in remaining_pre_inspections if pi.id not in used_pre_inspection_ids_in_run]
        for i in range(min(3, len(remaining_pre_inspections_for_cancel))):
            # Find an unused pre-inspection
            available_pre_inspections = [pi for pi in remaining_pre_inspections_for_cancel if pi.id not in used_pre_inspection_ids_in_run]
            if not available_pre_inspections:
                break
                
            pre_inspection = random.choice(available_pre_inspections)
            used_pre_inspection_ids_in_run.add(pre_inspection.id)
            vehicle = pre_inspection.vehicle
            scheduled_date = today - timedelta(days=random.randint(10, 90))
            
            PMS.objects.create(
                vehicle=vehicle,
                service_type='General Inspection',
                scheduled_date=scheduled_date,
                completed_date=None,
                mileage_at_service=(vehicle.current_mileage or 0) + random.randint(-500, 500),
                next_service_mileage=None,
                cost=None,
                provider=None,
                technician=None,
                description='PMS was cancelled',
                notes='Cancelled due to vehicle unavailability',
                status='Cancelled',
                pre_inspection=pre_inspection,
                post_inspection=None,
                repair=None
            )
            created_cancelled += 1
        
        # Create Completed PMS (need post-inspections)
        # Use only PMS-type post-inspections whose pre-inspections haven't been used in this run
        pms_post_inspections = [
            pi for pi in post_inspections 
            if pi.report_type == 'pms' and pi.pre_inspection.id not in used_pre_inspection_ids_in_run
        ]
        num_completed = min(8, len(pms_post_inspections))
        for i in range(num_completed):
            # Find an available post-inspection with unused pre-inspection
            available_post_inspections = [
                pi for pi in pms_post_inspections 
                if pi.pre_inspection.id not in used_pre_inspection_ids_in_run
            ]
            if not available_post_inspections:
                break
                
            post_inspection = random.choice(available_post_inspections)
            pre_inspection = post_inspection.pre_inspection
            used_pre_inspection_ids_in_run.add(pre_inspection.id)
            vehicle = post_inspection.vehicle
            
            days_ago = random.randint(10, 180)
            scheduled_date = datetime.now().date() - timedelta(days=days_ago)
            completed_date = scheduled_date + timedelta(days=random.randint(1, 5))
            
            PMS.objects.create(
                vehicle=vehicle,
                service_type='General Inspection',
                scheduled_date=scheduled_date,
                completed_date=completed_date,
                mileage_at_service=(vehicle.current_mileage or 0) - random.randint(1000, 5000),
                next_service_mileage=(vehicle.current_mileage or 0) + random.randint(5000, 15000),
                cost=Decimal(str(random.randint(3000, 10000))),
                provider=random.choice(providers),
                technician=random.choice(technicians),
                description=random.choice(descriptions),
                notes='PMS completed successfully',
                status='Completed',
                pre_inspection=pre_inspection,
                post_inspection=post_inspection,
                repair=None
            )
            created_completed += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created_scheduled + created_in_progress + created_completed + created_overdue + created_cancelled} PMS records (Scheduled: {created_scheduled}, In Progress: {created_in_progress}, Completed: {created_completed}, Overdue: {created_overdue}, Cancelled: {created_cancelled})'))
        self.stdout.write(self.style.SUCCESS(f'      -> {created_scheduled + created_overdue} PMS records for Serviceable vehicles (will appear in "Near PMS" dashboard)'))

    def create_post_inspections(self):
        """Create post-inspection reports linked to pre-inspections"""
        # Get pre-inspections that are already used by repairs or PMS (from database)
        used_pre_inspection_ids = set()
        used_pre_inspection_ids.update(
            Repair.objects.exclude(pre_inspection__isnull=True)
                         .values_list('pre_inspection_id', flat=True)
        )
        used_pre_inspection_ids.update(
            PMS.objects.exclude(pre_inspection__isnull=True)
                      .values_list('pre_inspection_id', flat=True)
        )
        
        # Get post-inspections that are already used (their pre-inspections are already linked)
        used_post_inspection_ids = set()
        used_post_inspection_ids.update(
            Repair.objects.exclude(post_inspection__isnull=True)
                         .values_list('post_inspection_id', flat=True)
        )
        used_post_inspection_ids.update(
            PMS.objects.exclude(post_inspection__isnull=True)
                      .values_list('post_inspection_id', flat=True)
        )
        
        # Get available approved pre-inspections (not yet used and not linked to existing post-inspections)
        available_pre_inspections = list(PreInspectionReport.objects.filter(
            approved_by__isnull=False
        ).exclude(id__in=used_pre_inspection_ids))
        
        users = list(User.objects.all())
        
        if not available_pre_inspections or not users:
            self.stdout.write(self.style.WARNING('  [-] Skipping post-inspections (missing available pre-inspections)'))
            return
        
        satisfaction_choices = ['excellent', 'good', 'satisfactory', 'needs_improvement']
        condition_choices = ['excellent', 'good', 'fair']
        
        created = 0
        # Split between repair and PMS types
        repair_pre_inspections = [pi for pi in available_pre_inspections if pi.report_type == 'repair']
        pms_pre_inspections = [pi for pi in available_pre_inspections if pi.report_type == 'pms']
        
        # Create post-inspections for repairs (10 total)
        # Only create if we haven't exceeded and pre-inspection is available
        for pre_inspection in repair_pre_inspections[:10]:
            if pre_inspection.id in used_pre_inspection_ids:
                continue
            post_inspection = PostInspectionReport.objects.create(
                vehicle=pre_inspection.vehicle,
                report_type=pre_inspection.report_type,
                inspected_by=random.choice(users),
                pre_inspection=pre_inspection,
                work_completed_satisfactorily=True,
                quality_of_work=random.choice(satisfaction_choices),
                timeliness=random.choice(satisfaction_choices),
                cleanliness=random.choice(satisfaction_choices),
                engine_condition=random.choice(condition_choices),
                transmission_condition=random.choice(condition_choices),
                brakes_condition=random.choice(condition_choices),
                suspension_condition=random.choice(condition_choices),
                electrical_condition=random.choice(condition_choices),
                body_condition=random.choice(condition_choices),
                tires_condition=random.choice(condition_choices),
                lights_condition=random.choice(condition_choices),
                test_drive_performed=True,
                test_drive_distance=random.randint(5, 25),
                test_drive_notes='Test drive completed successfully. Vehicle performed well.',
                remaining_issues='No remaining issues identified. All work completed satisfactorily.',
                future_recommendations='Continue regular maintenance schedule. Monitor condition regularly.',
                warranty_notes='Standard warranty applies. Contact service center if issues arise.',
                approved_by=random.choice(users),
                approval_date=timezone.now() - timedelta(days=random.randint(0, 10)),
                approval_notes='Post-inspection approved. Work completed to standards.'
            )
            created += 1
        
        # Create post-inspections for PMS (10 total)
        # Only create if we haven't exceeded and pre-inspection is available
        for pre_inspection in pms_pre_inspections[:10]:
            if pre_inspection.id in used_pre_inspection_ids:
                continue
            post_inspection = PostInspectionReport.objects.create(
                vehicle=pre_inspection.vehicle,
                report_type=pre_inspection.report_type,
                inspected_by=random.choice(users),
                pre_inspection=pre_inspection,
                work_completed_satisfactorily=True,
                quality_of_work=random.choice(satisfaction_choices),
                timeliness=random.choice(satisfaction_choices),
                cleanliness=random.choice(satisfaction_choices),
                engine_condition=random.choice(condition_choices),
                transmission_condition=random.choice(condition_choices),
                brakes_condition=random.choice(condition_choices),
                suspension_condition=random.choice(condition_choices),
                electrical_condition=random.choice(condition_choices),
                body_condition=random.choice(condition_choices),
                tires_condition=random.choice(condition_choices),
                lights_condition=random.choice(condition_choices),
                test_drive_performed=True,
                test_drive_distance=random.randint(5, 20),
                test_drive_notes='Test drive completed successfully. Vehicle ready for use.',
                remaining_issues='No remaining issues. Vehicle is in good condition.',
                future_recommendations='Schedule next PMS according to mileage or time interval.',
                warranty_notes='Maintenance warranty in effect.',
                approved_by=random.choice(users),
                approval_date=timezone.now() - timedelta(days=random.randint(0, 10)),
                approval_notes='Post-inspection approved. PMS completed successfully.'
            )
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} post-inspection reports (Repair: {min(10, len(repair_pre_inspections))}, PMS: {min(10, len(pms_pre_inspections))})'))

    def create_notifications(self):
        """Create notifications"""
        users = list(User.objects.all())
        
        if not users:
            self.stdout.write(self.style.WARNING('  [-] Skipping notifications (no users)'))
            return
        
        notifications_data = [
            ('PMS Reminder', 'Vehicle PMS is due for maintenance within 1 month', 'pms_reminder', 'medium'),
            ('Repair Completed', 'Repair has been completed successfully', 'repair_completed', 'low'),
            ('Vehicle Status Change', 'Vehicle status changed to Under Repair', 'vehicle_status', 'high'),
            ('Overdue PMS', 'Vehicle PMS is overdue and needs attention', 'pms_overdue', 'high'),
            ('General Notification', 'System maintenance scheduled for next week', 'general', 'low'),
            ('Inspection Approved', 'Pre-inspection report has been approved', 'inspection_approved', 'medium'),
            ('PMS Scheduled', 'New PMS has been scheduled for your vehicle', 'pms_scheduled', 'low'),
        ]
        
        created = 0
        for title, message, ntype, priority in notifications_data * 5:  # Create 35 notifications
            Notification.objects.create(
                user=random.choice(users),
                notification_type=ntype,
                title=title,
                message=message,
                priority=priority,
                is_read=random.choice([True, True, False]),  # 67% read
            )
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {created} notifications'))

    def print_summary(self):
        """Print database summary"""
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('DATABASE SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        self.stdout.write(f'\n  Users: {User.objects.count()} (Active: {User.objects.filter(status="active").count()}, Inactive: {User.objects.filter(status="inactive").count()})')
        self.stdout.write(f'  Divisions: {Division.objects.count()}')
        self.stdout.write(f'  Drivers: {Driver.objects.count()}')
        self.stdout.write(f'  Vehicles: {Vehicle.objects.count()}')
        self.stdout.write(f'    - Serviceable: {Vehicle.objects.filter(status="Serviceable").count()}')
        self.stdout.write(f'    - Under Repair: {Vehicle.objects.filter(status="Under Repair").count()}')
        self.stdout.write(f'    - Unserviceable: {Vehicle.objects.filter(status="Unserviceable").count()}')
        self.stdout.write(f'  Repair Shops: {RepairShop.objects.count()} (Active: {RepairShop.objects.filter(is_active=True).count()})')
        self.stdout.write(f'  Repair Parts: {RepairPart.objects.count()} (Active: {RepairPart.objects.filter(is_active=True).count()})')
        self.stdout.write(f'  Repairs: {Repair.objects.count()}')
        self.stdout.write(f'    - Ongoing: {Repair.objects.filter(status="Ongoing").count()}')
        self.stdout.write(f'    - Completed: {Repair.objects.filter(status="Completed").count()}')
        self.stdout.write(f'  Repair Part Items: {RepairPartItem.objects.count()}')
        self.stdout.write(f'  PMS Records: {PMS.objects.count()}')
        self.stdout.write(f'    - Scheduled: {PMS.objects.filter(status="Scheduled").count()}')
        self.stdout.write(f'    - In Progress: {PMS.objects.filter(status="In Progress").count()}')
        self.stdout.write(f'    - Completed: {PMS.objects.filter(status="Completed").count()}')
        self.stdout.write(f'    - Overdue: {PMS.objects.filter(status="Overdue").count()}')
        self.stdout.write(f'    - Cancelled: {PMS.objects.filter(status="Cancelled").count()}')
        self.stdout.write(f'  Pre-Inspections: {PreInspectionReport.objects.count()}')
        self.stdout.write(f'    - Approved: {PreInspectionReport.objects.filter(approved_by__isnull=False).count()}')
        self.stdout.write(f'    - Unapproved: {PreInspectionReport.objects.filter(approved_by__isnull=True).count()}')
        self.stdout.write(f'    - Repair type: {PreInspectionReport.objects.filter(report_type="repair").count()}')
        self.stdout.write(f'    - PMS type: {PreInspectionReport.objects.filter(report_type="pms").count()}')
        self.stdout.write(f'  Post-Inspections: {PostInspectionReport.objects.count()}')
        self.stdout.write(f'    - Approved: {PostInspectionReport.objects.filter(approved_by__isnull=False).count()}')
        self.stdout.write(f'    - Unapproved: {PostInspectionReport.objects.filter(approved_by__isnull=True).count()}')
        self.stdout.write(f'  Notifications: {Notification.objects.count()}')
