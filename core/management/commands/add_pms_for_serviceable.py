from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Vehicle, PMS, PreInspectionReport
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Add PMS records for Serviceable vehicles so they appear in dashboard'

    def handle(self, *args, **options):
        today = timezone.now().date()
        serviceable_vehicles = Vehicle.objects.filter(status='Serviceable')
        
        if serviceable_vehicles.count() == 0:
            self.stdout.write(self.style.WARNING('No Serviceable vehicles found.'))
            return
        
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.WARNING('No users found.'))
            return
        
        created_overdue = 0
        created_scheduled = 0
        
        for vehicle in serviceable_vehicles:
            # Create Overdue PMS if none exists
            if not PMS.objects.filter(vehicle=vehicle, status='Overdue').exists():
                # Create a pre-inspection for this PMS (or find unused one)
                pre_inspection_overdue = PreInspectionReport.objects.filter(
                    vehicle=vehicle,
                    report_type='pms',
                    approved_by__isnull=False
                ).exclude(
                    id__in=PMS.objects.exclude(pre_inspection__isnull=True)
                                   .values_list('pre_inspection_id', flat=True)
                ).first()
                
                if not pre_inspection_overdue:
                    pre_inspection_overdue = PreInspectionReport.objects.create(
                        vehicle=vehicle,
                        report_type='pms',
                        inspected_by=users[0],
                        engine_condition='good',
                        transmission_condition='good',
                        brakes_condition='good',
                        suspension_condition='good',
                        electrical_condition='good',
                        body_condition='good',
                        tires_condition='good',
                        lights_condition='good',
                        current_mileage=vehicle.current_mileage or 0,
                        fuel_level='half',
                        issues_found='',
                        safety_concerns='',
                        recommended_actions='',
                        approved_by=users[0],
                        approval_date=timezone.now(),
                        approval_notes='Auto-created for overdue PMS'
                    )
                
                PMS.objects.create(
                    vehicle=vehicle,
                    service_type='General Inspection',
                    scheduled_date=today - timedelta(days=5),
                    completed_date=None,
                    mileage_at_service=vehicle.current_mileage or 0,
                    next_service_mileage=(vehicle.current_mileage or 0) + 10000,
                    cost=None,
                    provider='AutoCare Service Center',
                    technician='',
                    description='Routine general inspection',
                    notes='PMS is overdue',
                    status='Overdue',
                    pre_inspection=pre_inspection_overdue,
                    post_inspection=None,
                    repair=None
                )
                created_overdue += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created Overdue PMS for {vehicle.plate_number}'))
            
            # Create Scheduled PMS if none exists
            if not PMS.objects.filter(vehicle=vehicle, status='Scheduled').exists():
                # Create a separate pre-inspection for this PMS
                pre_inspection_scheduled = PreInspectionReport.objects.filter(
                    vehicle=vehicle,
                    report_type='pms',
                    approved_by__isnull=False
                ).exclude(
                    id__in=PMS.objects.exclude(pre_inspection__isnull=True)
                                   .values_list('pre_inspection_id', flat=True)
                ).first()
                
                if not pre_inspection_scheduled:
                    pre_inspection_scheduled = PreInspectionReport.objects.create(
                        vehicle=vehicle,
                        report_type='pms',
                        inspected_by=users[0],
                        engine_condition='good',
                        transmission_condition='good',
                        brakes_condition='good',
                        suspension_condition='good',
                        electrical_condition='good',
                        body_condition='good',
                        tires_condition='good',
                        lights_condition='good',
                        current_mileage=vehicle.current_mileage or 0,
                        fuel_level='half',
                        issues_found='',
                        safety_concerns='',
                        recommended_actions='',
                        approved_by=users[0],
                        approval_date=timezone.now(),
                        approval_notes='Auto-created for scheduled PMS'
                    )
                
                PMS.objects.create(
                    vehicle=vehicle,
                    service_type='General Inspection',
                    scheduled_date=today + timedelta(days=10),
                    completed_date=None,
                    mileage_at_service=vehicle.current_mileage or 0,
                    next_service_mileage=(vehicle.current_mileage or 0) + 10000,
                    cost=None,
                    provider='AutoCare Service Center',
                    technician='',
                    description='Routine general inspection',
                    notes='Scheduled PMS',
                    status='Scheduled',
                    pre_inspection=pre_inspection_scheduled,
                    post_inspection=None,
                    repair=None
                )
                created_scheduled += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created Scheduled PMS for {vehicle.plate_number}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n[OK] Created {created_overdue} Overdue PMS and {created_scheduled} Scheduled PMS records'))
        self.stdout.write(self.style.SUCCESS('Vehicles Near PMS section should now show data on dashboard!'))

