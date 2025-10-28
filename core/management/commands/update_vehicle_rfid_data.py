from django.core.management.base import BaseCommand
from core.models import Vehicle
import random


class Command(BaseCommand):
    help = 'Update RFID and Fleet Card data for all vehicles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if data already exists'
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        vehicles = Vehicle.objects.all()
        updated_count = 0
        
        for vehicle in vehicles:
            updated = False
            
            # Add fleet card number if missing or if forced
            if not vehicle.fleet_card_number or force:
                plate_num = vehicle.plate_number.replace('-', '')
                if not vehicle.fleet_card_number or force:
                    vehicle.fleet_card_number = f'FC-{plate_num[-4:]}'
                    updated = True
            
            # Add RFID type if missing or if forced - do this first so we can generate the right RFID number
            if not vehicle.rfid_type or force:
                # Assign RFID type based on vehicle type
                if vehicle.vehicle_type in ['Motorcycle', 'Bicycle']:
                    vehicle.rfid_type = None  # Motorcycles and bicycles usually don't have RFID
                else:
                    # Assign either Autosweep or Easytrip
                    vehicle.rfid_type = random.choice(['Autosweep', 'Easytrip'])
                updated = True
                
                # Now generate RFID number based on the newly assigned type
                if vehicle.rfid_type:
                    plate_num = vehicle.plate_number.replace('-', '')
                    if vehicle.rfid_type == 'Autosweep':
                        vehicle.rfid_number = f'ASW-{plate_num[-4:]}'
                    else:  # Easytrip
                        vehicle.rfid_number = f'ETR-{plate_num[-4:]}'
                else:
                    vehicle.rfid_number = ''
                updated = True
            
            # Update gas station if needed or if forced
            if not vehicle.gas_station or force:
                if vehicle.rfid_type == 'Autosweep':
                    vehicle.gas_station = 'Shell'
                elif vehicle.rfid_type == 'Easytrip':
                    vehicle.gas_station = 'Petron'
                else:
                    vehicle.gas_station = random.choice(['Shell', 'Petron', 'Caltex', 'Total'])
                updated = True
            
            if updated:
                vehicle.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated {vehicle.plate_number}: '
                        f'RFID Number={vehicle.rfid_number or "None"}, RFID Type={vehicle.rfid_type or "None"}, Fleet Card={vehicle.fleet_card_number}, Gas={vehicle.gas_station}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nUpdated {updated_count} vehicles with RFID and Fleet Card information!')
        )
        
        # Show summary
        self.stdout.write('\nCurrent Vehicle RFID Data:')
        self.stdout.write('=' * 60)
        for vehicle in Vehicle.objects.all():
            self.stdout.write(
                f'{vehicle.plate_number} ({vehicle.brand} {vehicle.model}): '
                f'RFID Number={vehicle.rfid_number or "None"}, RFID Type={vehicle.rfid_type or "None"}, Fleet Card={vehicle.fleet_card_number}, Gas={vehicle.gas_station}'
            )

