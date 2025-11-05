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
            
            # Add RFID numbers if missing or if forced
            plate_num = vehicle.plate_number.replace('-', '')
            
            if not vehicle.rfid_autosweep_number or force:
                # Assign RFID number based on vehicle type
                if vehicle.vehicle_type in ['MOTORCYCLE']:
                    # Motorcycles usually don't have RFID
                    vehicle.rfid_autosweep_number = ''
                else:
                    # Randomly assign: 70% chance of having Autosweep RFID
                    if random.random() > 0.3:
                        vehicle.rfid_autosweep_number = f'ASW-{plate_num[-4:]}'
                    else:
                        vehicle.rfid_autosweep_number = ''
                updated = True
            
            if not vehicle.rfid_easytrip_number or force:
                # Assign RFID number based on vehicle type
                if vehicle.vehicle_type in ['MOTORCYCLE']:
                    # Motorcycles usually don't have RFID
                    vehicle.rfid_easytrip_number = ''
                else:
                    # Randomly assign: 70% chance of having Easytrip RFID
                    if random.random() > 0.3:
                        vehicle.rfid_easytrip_number = f'ETR-{plate_num[-4:]}'
                    else:
                        vehicle.rfid_easytrip_number = ''
                updated = True
            
            # Update gas station if needed or if forced
            if not vehicle.gas_station or force:
                has_autosweep = bool(vehicle.rfid_autosweep_number)
                has_easytrip = bool(vehicle.rfid_easytrip_number)
                
                if has_autosweep and has_easytrip:
                    vehicle.gas_station = random.choice(['Shell', 'Petron'])  # Both support both
                elif has_autosweep:
                    vehicle.gas_station = 'Shell'
                elif has_easytrip:
                    vehicle.gas_station = 'Petron'
                else:
                    vehicle.gas_station = random.choice(['Shell', 'Petron', 'Caltex', 'Total'])
                updated = True
            
            if updated:
                vehicle.save()
                updated_count += 1
                rfid_info = []
                if vehicle.rfid_autosweep_number:
                    rfid_info.append(f'Autosweep: {vehicle.rfid_autosweep_number}')
                if vehicle.rfid_easytrip_number:
                    rfid_info.append(f'Easytrip: {vehicle.rfid_easytrip_number}')
                rfid_str = ', '.join(rfid_info) if rfid_info else 'None'
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated {vehicle.plate_number}: '
                        f'RFID Numbers={rfid_str}, Fleet Card={vehicle.fleet_card_number}, Gas={vehicle.gas_station}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nUpdated {updated_count} vehicles with RFID and Fleet Card information!')
        )
        
        # Show summary
        self.stdout.write('\nCurrent Vehicle RFID Data:')
        self.stdout.write('=' * 60)
        for vehicle in Vehicle.objects.all():
            rfid_info = []
            if vehicle.rfid_autosweep_number:
                rfid_info.append(f'Autosweep: {vehicle.rfid_autosweep_number}')
            if vehicle.rfid_easytrip_number:
                rfid_info.append(f'Easytrip: {vehicle.rfid_easytrip_number}')
            rfid_str = ', '.join(rfid_info) if rfid_info else 'None'
            
            self.stdout.write(
                f'{vehicle.plate_number} ({vehicle.brand} {vehicle.model}): '
                f'RFID Numbers={rfid_str}, Fleet Card={vehicle.fleet_card_number}, Gas={vehicle.gas_station}'
            )

