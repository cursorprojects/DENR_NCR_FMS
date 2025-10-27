from django.core.management.base import BaseCommand
from core.models import RepairShop, Repair
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Add sample repair shop data and link to existing repairs'

    def handle(self, *args, **options):
        self.stdout.write('Adding sample repair shop data...')
        
        # Sample repair shops data
        repair_shops_data = [
            {
                'name': 'AutoCare Plus',
                'address': '123 Main Street, Quezon City, Metro Manila',
                'phone': '+63 2 1234-5678',
                'email': 'info@autocareplus.com',
                'contact_person': 'Juan Dela Cruz',
                'is_active': True
            },
            {
                'name': 'Metro Motors Service Center',
                'address': '456 EDSA, Mandaluyong City, Metro Manila',
                'phone': '+63 2 2345-6789',
                'email': 'service@metromotors.com',
                'contact_person': 'Maria Santos',
                'is_active': True
            },
            {
                'name': 'Fleet Maintenance Co.',
                'address': '789 Ortigas Avenue, Pasig City, Metro Manila',
                'phone': '+63 2 3456-7890',
                'email': 'fleet@maintenance.com',
                'contact_person': 'Pedro Rodriguez',
                'is_active': True
            },
            {
                'name': 'Quick Fix Garage',
                'address': '321 Taft Avenue, Manila City',
                'phone': '+63 2 4567-8901',
                'email': 'quickfix@garage.com',
                'contact_person': 'Ana Garcia',
                'is_active': True
            },
            {
                'name': 'Professional Auto Repair',
                'address': '654 Commonwealth Avenue, Quezon City',
                'phone': '+63 2 5678-9012',
                'email': 'pro@autorepair.com',
                'contact_person': 'Carlos Mendoza',
                'is_active': True
            },
            {
                'name': 'Express Service Center',
                'address': '987 Ayala Avenue, Makati City',
                'phone': '+63 2 6789-0123',
                'email': 'express@service.com',
                'contact_person': 'Lisa Torres',
                'is_active': True
            },
            {
                'name': 'Reliable Motors',
                'address': '147 Shaw Boulevard, Mandaluyong City',
                'phone': '+63 2 7890-1234',
                'email': 'reliable@motors.com',
                'contact_person': 'Roberto Silva',
                'is_active': True
            },
            {
                'name': 'City Auto Works',
                'address': '258 Timog Avenue, Quezon City',
                'phone': '+63 2 8901-2345',
                'email': 'city@autoworks.com',
                'contact_person': 'Carmen Reyes',
                'is_active': True
            },
            {
                'name': 'Budget Repair Shop',
                'address': '369 Rizal Avenue, Manila City',
                'phone': '+63 2 9012-3456',
                'email': 'budget@repair.com',
                'contact_person': 'Miguel Lopez',
                'is_active': True
            },
            {
                'name': 'Premium Auto Service',
                'address': '741 BGC, Taguig City',
                'phone': '+63 2 0123-4567',
                'email': 'premium@autoservice.com',
                'contact_person': 'Isabella Cruz',
                'is_active': True
            }
        ]
        
        # Create repair shops
        created_shops = []
        for shop_data in repair_shops_data:
            shop, created = RepairShop.objects.get_or_create(
                name=shop_data['name'],
                defaults=shop_data
            )
            if created:
                created_shops.append(shop)
                self.stdout.write(f'Created repair shop: {shop.name}')
            else:
                self.stdout.write(f'Repair shop already exists: {shop.name}')
        
        # Link existing repairs to random repair shops
        repairs = Repair.objects.all()
        if repairs.exists():
            self.stdout.write(f'Linking {repairs.count()} existing repairs to repair shops...')
            
            for repair in repairs:
                if not repair.repair_shop_id:  # Only update if repair_shop_id is empty
                    # Randomly assign a repair shop
                    random_shop = random.choice(RepairShop.objects.filter(is_active=True))
                    repair.repair_shop = random_shop
                    repair.save()
                    self.stdout.write(f'Linked repair {repair.id} to {random_shop.name}')
        
        # Add some inactive repair shops for variety
        inactive_shops_data = [
            {
                'name': 'Old Town Garage',
                'address': '555 Old Street, Manila City',
                'phone': '+63 2 1111-2222',
                'email': 'old@garage.com',
                'contact_person': 'Elder Martinez',
                'is_active': False
            },
            {
                'name': 'Closed Service Center',
                'address': '999 Closed Road, Pasay City',
                'phone': '+63 2 3333-4444',
                'email': 'closed@service.com',
                'contact_person': 'Former Owner',
                'is_active': False
            }
        ]
        
        for shop_data in inactive_shops_data:
            shop, created = RepairShop.objects.get_or_create(
                name=shop_data['name'],
                defaults=shop_data
            )
            if created:
                self.stdout.write(f'Created inactive repair shop: {shop.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully added {len(created_shops)} new repair shops and linked existing repairs!'
            )
        )
        
        # Display summary
        total_shops = RepairShop.objects.count()
        active_shops = RepairShop.objects.filter(is_active=True).count()
        repairs_with_shops = Repair.objects.exclude(repair_shop__isnull=True).count()
        
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'- Total repair shops: {total_shops}')
        self.stdout.write(f'- Active repair shops: {active_shops}')
        self.stdout.write(f'- Repairs with assigned shops: {repairs_with_shops}')
