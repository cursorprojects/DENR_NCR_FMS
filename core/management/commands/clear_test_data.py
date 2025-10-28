from django.core.management.base import BaseCommand
from core.models import Repair, RepairPartItem, RepairShop, RepairPart, Division, Driver, Vehicle
from django.db import transaction


class Command(BaseCommand):
    help = 'Clear all test data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmation',
            type=str,
            help='Confirmation text to proceed with deletion'
        )

    def handle(self, *args, **options):
        confirmation = options.get('confirmation')
        
        if not confirmation:
            self.stdout.write(self.style.WARNING(
                'This command will DELETE ALL DATA in the database!'
            ))
            self.stdout.write(self.style.ERROR(
                'Run with --confirmation yes to proceed.'
            ))
            return
        
        if confirmation.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Deletion cancelled.'))
            return
        
        try:
            with transaction.atomic():
                # Count records before deletion
                repairs_count = Repair.objects.count()
                repair_parts_count = RepairPartItem.objects.count()
                vehicles_count = Vehicle.objects.count()
                drivers_count = Driver.objects.count()
                shops_count = RepairShop.objects.count()
                parts_count = RepairPart.objects.count()
                divisions_count = Division.objects.count()
                
                # Delete in order of dependencies
                self.stdout.write('Deleting repairs and parts...')
                RepairPartItem.objects.all().delete()
                repairs_count_deleted = Repair.objects.all().delete()[0]
                
                self.stdout.write('Deleting vehicles...')
                vehicles_count_deleted = Vehicle.objects.all().delete()[0]
                
                self.stdout.write('Deleting drivers...')
                drivers_count_deleted = Driver.objects.all().delete()[0]
                
                self.stdout.write('Deleting repair shops...')
                shops_count_deleted = RepairShop.objects.all().delete()[0]
                
                self.stdout.write('Deleting repair parts...')
                parts_count_deleted = RepairPart.objects.all().delete()[0]
                
                self.stdout.write('Deleting divisions...')
                divisions_count_deleted = Division.objects.all().delete()[0]
                
                # Summary
                self.stdout.write('\n' + '='*60)
                self.stdout.write(self.style.SUCCESS('Data Deletion Summary:'))
                self.stdout.write('='*60)
                self.stdout.write(f'Repairs deleted:        {repairs_count_deleted}')
                self.stdout.write(f'Vehicles deleted:       {vehicles_count_deleted}')
                self.stdout.write(f'Drivers deleted:        {drivers_count_deleted}')
                self.stdout.write(f'Repair shops deleted:   {shops_count_deleted}')
                self.stdout.write(f'Repair parts deleted:   {parts_count_deleted}')
                self.stdout.write(f'Divisions deleted:      {divisions_count_deleted}')
                self.stdout.write('='*60)
                
                self.stdout.write(
                    self.style.SUCCESS('\nAll test data has been successfully deleted!')
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during deletion: {str(e)}'))

