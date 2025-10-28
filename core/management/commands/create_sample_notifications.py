from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Notification, CustomUser, PMS, Vehicle


class Command(BaseCommand):
    help = 'Create sample notifications for testing'

    def handle(self, *args, **options):
        # Get all users
        users = CustomUser.objects.filter(is_active=True)
        
        if not users.exists():
            self.stdout.write(
                self.style.ERROR('No active users found. Please create a user first.')
            )
            return

        # Clear existing notifications
        Notification.objects.all().delete()
        self.stdout.write('Cleared existing notifications.')

        # Get some vehicles and PMS records for context
        vehicles = Vehicle.objects.all()[:3]
        pms_records = PMS.objects.all()[:3]

        created_count = 0

        # Create sample notifications
        sample_notifications = [
            {
                'notification_type': 'pms_reminder',
                'title': 'PMS Due Today: ABC-1234',
                'message': 'The PMS for ABC-1234 (Toyota Vios) is scheduled for today (October 28, 2024). Please ensure the vehicle is ready for service.',
                'priority': 'urgent',
                'related_object_id': pms_records[0].id if pms_records else None,
                'related_object_type': 'PMS' if pms_records else None,
            },
            {
                'notification_type': 'pms_reminder',
                'title': 'PMS Tomorrow: DEF-9012',
                'message': 'The PMS for DEF-9012 (Toyota RAV4) is scheduled for tomorrow (October 29, 2024). Please prepare the vehicle for service.',
                'priority': 'high',
                'related_object_id': pms_records[1].id if len(pms_records) > 1 else None,
                'related_object_type': 'PMS' if len(pms_records) > 1 else None,
            },
            {
                'notification_type': 'pms_reminder',
                'title': 'PMS in 2 Days: GHI-3456',
                'message': 'The PMS for GHI-3456 (Toyota Hilux) is scheduled in 2 days (October 30, 2024). Please plan accordingly.',
                'priority': 'medium',
                'related_object_id': pms_records[2].id if len(pms_records) > 2 else None,
                'related_object_type': 'PMS' if len(pms_records) > 2 else None,
            },
            {
                'notification_type': 'pms_overdue',
                'title': 'PMS Overdue: JKL-7890',
                'message': 'The PMS for JKL-7890 (Toyota Grandia) is 5 days overdue (scheduled for October 23, 2024). Please reschedule immediately.',
                'priority': 'urgent',
                'related_object_id': None,
                'related_object_type': None,
            },
            {
                'notification_type': 'repair_completed',
                'title': 'Repair Completed: XYZ-5678',
                'message': 'The repair for XYZ-5678 (Honda Motorcycle) has been completed successfully. Total cost: ₱2,500.00',
                'priority': 'medium',
                'related_object_id': None,
                'related_object_type': None,
            },
            {
                'notification_type': 'vehicle_status',
                'title': 'Vehicle Status Changed: ABC-1234',
                'message': 'Vehicle ABC-1234 (Toyota Vios) status has been changed from "Under Repair" to "Serviceable".',
                'priority': 'medium',
                'related_object_id': vehicles[0].id if vehicles else None,
                'related_object_type': 'Vehicle' if vehicles else None,
            },
            {
                'notification_type': 'general',
                'title': 'System Maintenance Scheduled',
                'message': 'System maintenance is scheduled for November 1, 2024, from 2:00 AM to 4:00 AM. Please save your work before this time.',
                'priority': 'low',
                'related_object_id': None,
                'related_object_type': None,
            },
            {
                'notification_type': 'pms_reminder',
                'title': 'PMS Due Today: PMS-0001',
                'message': 'The PMS for PMS-0001 (Toyota Altis) is scheduled for today (October 28, 2024). This vehicle has never had PMS before.',
                'priority': 'urgent',
                'related_object_id': None,
                'related_object_type': None,
            },
            {
                'notification_type': 'pms_overdue',
                'title': 'PMS Overdue: PMS-0002',
                'message': 'The PMS for PMS-0002 (Toyota Fortuner) is 8 months overdue (scheduled for February 28, 2024). Immediate attention required.',
                'priority': 'urgent',
                'related_object_id': None,
                'related_object_type': None,
            },
            {
                'notification_type': 'general',
                'title': 'Monthly Report Available',
                'message': 'The monthly fleet management report for October 2024 is now available. Click here to view the detailed report.',
                'priority': 'low',
                'related_object_id': None,
                'related_object_type': None,
            }
        ]

        # Create notifications for all users
        for user in users:
            for i, notif_data in enumerate(sample_notifications):
                # Create notifications with different timestamps
                created_at = timezone.now() - timedelta(hours=i*2)  # Spread over time
                
                notification = Notification.objects.create(
                    user=user,
                    notification_type=notif_data['notification_type'],
                    title=notif_data['title'],
                    message=notif_data['message'],
                    priority=notif_data['priority'],
                    related_object_id=notif_data['related_object_id'] or None,
                    related_object_type=notif_data['related_object_type'] or '',
                    created_at=created_at,
                    is_read=False  # Make them unread for testing
                )
                
                created_count += 1
                self.stdout.write(f'Created notification: {notification.title}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} sample notifications!'
            )
        )
        
        # Show summary
        urgent_count = Notification.objects.filter(priority='urgent').count()
        high_count = Notification.objects.filter(priority='high').count()
        medium_count = Notification.objects.filter(priority='medium').count()
        low_count = Notification.objects.filter(priority='low').count()
        
        self.stdout.write(f'\nNotification Summary:')
        self.stdout.write(f'  Urgent: {urgent_count}')
        self.stdout.write(f'  High: {high_count}')
        self.stdout.write(f'  Medium: {medium_count}')
        self.stdout.write(f'  Low: {low_count}')
        self.stdout.write(f'  Total: {Notification.objects.count()}')
        
        self.stdout.write(
            self.style.SUCCESS(
                '\nYou should now see notifications in the notification bell!'
            )
        )
