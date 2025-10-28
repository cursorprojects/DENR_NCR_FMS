from django.core.management.base import BaseCommand
from core.models import Vehicle, PMS, Repair, RepairPartItem


class Command(BaseCommand):
    help = 'Clear PMS test vehicles and their related data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting'
        )

    def handle(self, *args, **options):
        # Find PMS test vehicles
        pms_test_vehicles = Vehicle.objects.filter(plate_number__startswith='PMS-')
        
        if not pms_test_vehicles.exists():
            self.stdout.write(
                self.style.WARNING('No PMS test vehicles found to delete.')
            )
            return

        if not options['confirm']:
            confirm = input(
                f'Are you sure you want to delete {pms_test_vehicles.count()} PMS test vehicles '
                f'and all their related data? This action cannot be undone. (yes/no): '
            )
            if confirm.lower() != 'yes':
                self.stdout.write('Operation cancelled.')
                return

        deleted_count = 0
        deleted_pms = 0
        deleted_repairs = 0
        deleted_parts = 0

        for vehicle in pms_test_vehicles:
            # Delete related PMS records
            pms_records = PMS.objects.filter(vehicle=vehicle)
            deleted_pms += pms_records.count()
            pms_records.delete()

            # Delete related repairs and parts
            repairs = Repair.objects.filter(vehicle=vehicle)
            for repair in repairs:
                # Delete repair parts
                parts = RepairPartItem.objects.filter(repair=repair)
                deleted_parts += parts.count()
                parts.delete()
            
            deleted_repairs += repairs.count()
            repairs.delete()

            # Delete the vehicle
            vehicle.delete()
            deleted_count += 1
            self.stdout.write(f'Deleted vehicle: {vehicle.plate_number}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully deleted:\n'
                f'  - {deleted_count} vehicles\n'
                f'  - {deleted_pms} PMS records\n'
                f'  - {deleted_repairs} repair records\n'
                f'  - {deleted_parts} repair parts'
            )
        )
