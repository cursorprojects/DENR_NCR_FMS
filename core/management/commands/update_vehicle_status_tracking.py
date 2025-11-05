from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Vehicle, CustomUser
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Update existing vehicles with status tracking fields'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get vehicles that don't have status tracking fields set
        vehicles_to_update = Vehicle.objects.filter(
            status_changed_at__isnull=True
        )
        
        if not vehicles_to_update.exists():
            self.stdout.write(
                self.style.SUCCESS('All vehicles already have status tracking fields set!')
            )
            return
        
        # Get a user for status tracking (use first super admin or create one)
        admin_user = CustomUser.objects.filter(role='super_admin').first()
        if not admin_user:
            admin_user = CustomUser.objects.first()
        
        if not admin_user:
            self.stdout.write(
                self.style.ERROR('No users found. Please create a user first.')
            )
            return
        
        updated_count = 0
        
        for vehicle in vehicles_to_update:
            if dry_run:
                self.stdout.write(
                    f'Would update vehicle: {vehicle.plate_number} '
                    f'({vehicle.brand} {vehicle.model}) - Status: {vehicle.status}'
                )
            else:
                # Set status tracking fields
                vehicle.status_changed_at = timezone.now() - timedelta(days=random.randint(1, 90))
                vehicle.status_changed_by = admin_user
                vehicle.status_change_reason = f'Initial status tracking setup - Status: {vehicle.status}'
                vehicle.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated vehicle: {vehicle.plate_number} '
                        f'({vehicle.brand} {vehicle.model}) - Status: {vehicle.status}'
                    )
                )
            
            updated_count += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\nDry run complete. Would update {updated_count} vehicles.'
                )
            )
            self.stdout.write('Run without --dry-run to apply changes.')
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully updated {updated_count} vehicles with status tracking fields!'
                )
            )
        
        self.stdout.write(f'\nTotal vehicles in database: {Vehicle.objects.count()}')
        self.stdout.write(f'Vehicles with status tracking: {Vehicle.objects.filter(status_changed_at__isnull=False).count()}')
        self.stdout.write(f'Vehicles without status tracking: {Vehicle.objects.filter(status_changed_at__isnull=True).count()}')
