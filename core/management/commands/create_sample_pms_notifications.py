from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import PMS, Vehicle


class Command(BaseCommand):
    help = 'Create sample PMS records with scheduled dates for testing notifications'

    def handle(self, *args, **options):
        # Get vehicles
        vehicles = Vehicle.objects.filter(status='Serviceable')
        
        if not vehicles.exists():
            self.stdout.write(
                self.style.ERROR('No serviceable vehicles found. Please add vehicles first.')
            )
            return

        # Create PMS records for different scenarios
        today = timezone.now().date()
        
        # Scenario 1: PMS due today
        vehicle_today = vehicles.first()
        pms_today = PMS.objects.create(
            vehicle=vehicle_today,
            service_type='General Inspection',
            scheduled_date=today,
            status='Scheduled',
            provider='Test Auto Service',
            technician='Test Technician',
            description='PMS scheduled for today - urgent notification',
            notes='This PMS is due today'
        )
        self.stdout.write(f'Created PMS for today: {vehicle_today.plate_number}')

        # Scenario 2: PMS due tomorrow
        if vehicles.count() > 1:
            vehicle_tomorrow = vehicles[1]
            pms_tomorrow = PMS.objects.create(
                vehicle=vehicle_tomorrow,
                service_type='General Inspection',
                scheduled_date=today + timedelta(days=1),
                status='Scheduled',
                provider='Test Auto Service',
                technician='Test Technician',
                description='PMS scheduled for tomorrow - high priority notification',
                notes='This PMS is due tomorrow'
            )
            self.stdout.write(f'Created PMS for tomorrow: {vehicle_tomorrow.plate_number}')

        # Scenario 3: PMS due in 2 days
        if vehicles.count() > 2:
            vehicle_2days = vehicles[2]
            pms_2days = PMS.objects.create(
                vehicle=vehicle_2days,
                service_type='General Inspection',
                scheduled_date=today + timedelta(days=2),
                status='Scheduled',
                provider='Test Auto Service',
                technician='Test Technician',
                description='PMS scheduled in 2 days - medium priority notification',
                notes='This PMS is due in 2 days'
            )
            self.stdout.write(f'Created PMS for 2 days: {vehicle_2days.plate_number}')

        # Scenario 4: Overdue PMS
        if vehicles.count() > 3:
            vehicle_overdue = vehicles[3]
            pms_overdue = PMS.objects.create(
                vehicle=vehicle_overdue,
                service_type='General Inspection',
                scheduled_date=today - timedelta(days=5),  # 5 days overdue
                status='Scheduled',
                provider='Test Auto Service',
                technician='Test Technician',
                description='Overdue PMS - urgent notification',
                notes='This PMS is 5 days overdue'
            )
            self.stdout.write(f'Created overdue PMS: {vehicle_overdue.plate_number}')

        self.stdout.write(
            self.style.SUCCESS(
                '\nSample PMS records created for notification testing!'
            )
        )
        self.stdout.write(
            'Run "python manage.py generate_pms_notifications" to create notifications.'
        )
