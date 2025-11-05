from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import (
    Division, Driver, Vehicle, RepairShop, RepairPart, Repair, 
    PMS, PreInspectionReport, PostInspectionReport, Notification, ActivityLog
)
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create comprehensive sample data for Fleet Management System'

    def handle(self, *args, **options):
        self.stdout.write('Creating comprehensive sample data...')
        
        # Create additional users with different permission sets
        self.create_users()
        
        # Create additional divisions
        self.create_divisions()
        
        # Create additional drivers
        self.create_drivers()
        
        # Create additional vehicles
        self.create_vehicles()
        
        # Create additional repair shops
        self.create_repair_shops()
        
        # Create additional repair parts
        self.create_repair_parts()
        
        # Create notifications
        self.create_notifications()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created comprehensive sample data!')
        )

    def create_users(self):
        """Create additional users with different permission sets"""
        users_data = [
            {
                'username': 'fleet_manager',
                'email': 'fleet.manager@denr.gov.ph',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'status': 'active',
                'phone': '+63-912-345-6789',
                'permissions': {
                    'can_view_vehicles': True,
                    'can_add_vehicles': True,
                    'can_edit_vehicles': True,
                    'can_view_repairs': True,
                    'can_add_repairs': True,
                    'can_edit_repairs': True,
                    'can_complete_repairs': True,
                    'can_view_pms': True,
                    'can_add_pms': True,
                    'can_edit_pms': True,
                    'can_complete_pms': True,
                    'can_view_inspections': True,
                    'can_add_inspections': True,
                    'can_edit_inspections': True,
                    'can_approve_inspections': True,
                    'can_view_reports': True,
                    'can_view_operational_status': True,
                }
            },
            {
                'username': 'encoder_staff',
                'email': 'encoder@denr.gov.ph',
                'first_name': 'Michael',
                'last_name': 'Brown',
                'status': 'active',
                'phone': '+63-923-456-7890',
                'permissions': {
                    'can_view_vehicles': True,
                    'can_add_vehicles': True,
                    'can_edit_vehicles': True,
                    'can_view_repairs': True,
                    'can_add_repairs': True,
                    'can_view_pms': True,
                    'can_add_pms': True,
                    'can_view_inspections': True,
                    'can_add_inspections': True,
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
                    'can_view_inspections': True,
                    'can_add_inspections': True,
                    'can_edit_inspections': True,
                    'can_approve_inspections': True,
                }
            }
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
                # Set permissions
                for perm, value in user_data['permissions'].items():
                    setattr(user, perm, value)
                user.save()
                self.stdout.write(f'Created user: {user.username}')

    def create_divisions(self):
        """Create additional divisions"""
        divisions = [
            'Environmental Management Division',
            'Forest Management Division',
            'Mining and Geosciences Division',
            'Biodiversity Management Division',
            'Climate Change Division',
            'Legal Division',
            'Human Resources Division',
            'Information Technology Division',
            'Procurement Division',
            'Internal Audit Division'
        ]
        
        for div_name in divisions:
            division, created = Division.objects.get_or_create(
                name=div_name,
                defaults={'description': f'Description for {div_name}'}
            )
            if created:
                self.stdout.write(f'Created division: {division.name}')

    def create_drivers(self):
        """Create additional drivers"""
        drivers_data = [
            ('Roberto Martinez', 'D06-678901', '+63-945-678-9012', 'roberto.martinez@denr.gov.ph'),
            ('Elena Fernandez', 'D07-789012', '+63-956-789-0123', 'elena.fernandez@denr.gov.ph'),
            ('Antonio Cruz', 'D08-890123', '+63-967-890-1234', 'antonio.cruz@denr.gov.ph'),
            ('Isabella Torres', 'D09-901234', '+63-978-901-2345', 'isabella.torres@denr.gov.ph'),
            ('Fernando Ramos', 'D10-012345', '+63-989-012-3456', 'fernando.ramos@denr.gov.ph'),
            ('Gabriela Morales', 'D11-123456', '+63-990-123-4567', 'gabriela.morales@denr.gov.ph'),
            ('Ricardo Herrera', 'D12-234567', '+63-901-234-5678', 'ricardo.herrera@denr.gov.ph'),
            ('Patricia Jimenez', 'D13-345678', '+63-912-345-6789', 'patricia.jimenez@denr.gov.ph'),
        ]
        
        for name, license_num, phone, email in drivers_data:
            driver, created = Driver.objects.get_or_create(
                license_number=license_num,
                defaults={
                    'name': name,
                    'phone': phone,
                    'email': email
                }
            )
            if created:
                self.stdout.write(f'Created driver: {driver.name}')

    def create_vehicles(self):
        """Create additional vehicles"""
        divisions = list(Division.objects.all())
        drivers = list(Driver.objects.all())
        
        vehicles_data = [
            ('ABC-1234', 'Toyota', 'Camry', 2020, 'Sedan', 'Serviceable'),
            ('DEF-5678', 'Honda', 'CR-V', 2019, 'SUV', 'Serviceable'),
            ('GHI-9012', 'Ford', 'Everest', 2021, 'SUV', 'Under Repair'),
            ('JKL-3456', 'Mitsubishi', 'Montero', 2018, 'SUV', 'Serviceable'),
            ('MNO-7890', 'Nissan', 'Navara', 2020, 'Pickup Truck', 'Serviceable'),
            ('PQR-2468', 'Isuzu', 'D-Max', 2019, 'Pickup Truck', 'Unserviceable'),
            ('STU-1357', 'Hyundai', 'Accent', 2021, 'Sedan', 'Serviceable'),
            ('VWX-9753', 'Suzuki', 'Ertiga', 2020, 'Van', 'Serviceable'),
            ('YZA-8642', 'Chevrolet', 'Trailblazer', 2019, 'SUV', 'Under Repair'),
            ('BCD-7531', 'Mazda', 'CX-5', 2021, 'SUV', 'Serviceable'),
        ]
        
        for plate, brand, model, year, vtype, status in vehicles_data:
            vehicle, created = Vehicle.objects.get_or_create(
                plate_number=plate,
                defaults={
                    'brand': brand,
                    'model': model,
                    'year': year,
                    'vehicle_type': vtype,
                    'status': status,
                    'division': random.choice(divisions) if divisions else None,
                    'assigned_driver': random.choice(drivers) if drivers else None,
                    'date_acquired': datetime.now().date() - timedelta(days=random.randint(30, 1000)),
                    'current_mileage': random.randint(10000, 100000),
                    'acquisition_cost': random.randint(500000, 2000000),
                    'engine_number': f'ENG-{random.randint(100000, 999999)}',
                    'chassis_number': f'CHS-{random.randint(100000, 999999)}',
                    'color': random.choice(['White', 'Black', 'Silver', 'Blue', 'Red', 'Gray']),
                    'rfid_number': f'RFID-{random.randint(100000, 999999)}',
                    'fleet_card_number': f'FC-{random.randint(100000, 999999)}',
                    'gas_station': random.choice(['Shell', 'Petron', 'Caltex', 'Total']),
                }
            )
            if created:
                self.stdout.write(f'Created vehicle: {vehicle.plate_number}')

    def create_repair_shops(self):
        """Create additional repair shops"""
        shops_data = [
            ('Premium Auto Service', '123 Main St, Quezon City', '+63-2-123-4567', 'premium@email.com', 'John Smith'),
            ('Quick Fix Garage', '456 EDSA, Makati', '+63-2-234-5678', 'quickfix@email.com', 'Maria Garcia'),
            ('Reliable Motors', '789 Ortigas Ave, Pasig', '+63-2-345-6789', 'reliable@email.com', 'Carlos Rodriguez'),
            ('Expert Auto Care', '321 Taft Ave, Manila', '+63-2-456-7890', 'expert@email.com', 'Ana Martinez'),
            ('Professional Service', '654 Commonwealth Ave, QC', '+63-2-567-8901', 'pro@email.com', 'Luis Fernandez'),
        ]
        
        for name, address, phone, email, contact in shops_data:
            shop, created = RepairShop.objects.get_or_create(
                name=name,
                defaults={
                    'address': address,
                    'phone': phone,
                    'email': email,
                    'contact_person': contact,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created repair shop: {shop.name}')

    def create_repair_parts(self):
        """Create additional repair parts"""
        parts_data = [
            'Brake Pads', 'Brake Rotors', 'Brake Calipers', 'Brake Lines',
            'Clutch Disc', 'Clutch Pressure Plate', 'Clutch Master Cylinder',
            'Engine Oil Filter', 'Fuel Filter', 'Air Filter', 'Cabin Filter',
            'Spark Plugs', 'Ignition Coils', 'Distributor Cap', 'Rotor',
            'Timing Belt', 'Serpentine Belt', 'Water Pump', 'Thermostat',
            'Radiator', 'Radiator Hose', 'Coolant', 'Transmission Fluid',
            'Power Steering Fluid', 'Brake Fluid', 'Windshield Washer Fluid',
            'Shock Absorbers', 'Struts', 'Control Arms', 'Ball Joints',
            'Tie Rod Ends', 'CV Joints', 'Wheel Bearings', 'Hub Assembly',
            'Tires', 'Wheel Rims', 'Lug Nuts', 'Valve Stems',
            'Headlights', 'Taillights', 'Turn Signals', 'Fog Lights',
            'Windshield', 'Side Windows', 'Door Handles', 'Mirrors',
            'Seat Belts', 'Airbags', 'Steering Wheel', 'Gear Shift',
            'Dashboard', 'Instrument Cluster', 'Radio', 'Speakers',
            'Wiring Harness', 'Fuses', 'Relays', 'Battery',
            'Alternator', 'Starter Motor', 'Voltage Regulator',
            'ECU', 'Sensors', 'Actuators', 'Switches',
            'Door Locks', 'Window Motors', 'Sunroof Motor',
            'AC Compressor', 'AC Condenser', 'AC Evaporator',
            'AC Expansion Valve', 'AC Receiver Dryer', 'AC Refrigerant',
            'Heater Core', 'Blower Motor', 'AC Control Panel',
            'Exhaust Manifold', 'Catalytic Converter', 'Muffler',
            'Exhaust Pipes', 'O2 Sensors', 'EGR Valve',
            'PCV Valve', 'Vacuum Lines', 'Intake Manifold',
            'Throttle Body', 'Mass Air Flow Sensor', 'Idle Air Control Valve'
        ]
        
        for part_name in parts_data:
            part, created = RepairPart.objects.get_or_create(
                name=part_name,
                defaults={
                    'description': f'Description for {part_name}',
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created repair part: {part.name}')

    def create_notifications(self):
        """Create additional notifications"""
        users = list(User.objects.all())
        
        if not users:
            return
            
        notification_types = [
            'pms_reminder', 'pms_overdue', 'repair_completed',
            'vehicle_status', 'general'
        ]
        
        priorities = ['low', 'medium', 'high', 'urgent']
        
        notifications_data = [
            ('PMS Reminder', 'Vehicle PMS-0001 is due for maintenance'),
            ('Repair Completed', 'Repair for vehicle ABC-1234 has been completed'),
            ('Vehicle Status Change', 'Vehicle DEF-5678 status changed to Under Repair'),
            ('Overdue PMS', 'Vehicle GHI-9012 PMS is overdue'),
            ('General Notification', 'System maintenance scheduled for this weekend'),
            ('New User Added', 'New user has been added to the system'),
            ('Report Generated', 'Monthly report has been generated'),
            ('Inspection Required', 'Vehicle JKL-3456 requires inspection'),
            ('Fuel Card Expired', 'Fuel card for vehicle MNO-7890 has expired'),
            ('Insurance Renewal', 'Insurance for vehicle PQR-2468 needs renewal')
        ]
        
        for title, message in notifications_data:
            user = random.choice(users)
            notification = Notification.objects.create(
                user=user,
                notification_type=random.choice(notification_types),
                title=title,
                message=message,
                priority=random.choice(priorities),
                is_read=random.choice([True, False]),
                related_object_id=random.randint(1, 100),
                related_object_type=random.choice(['Vehicle', 'Repair', 'PMS', 'User'])
            )
            self.stdout.write(f'Created notification: {notification.title}')
