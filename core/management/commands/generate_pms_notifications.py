from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import PMS, Notification, CustomUser


class Command(BaseCommand):
    help = 'Generate PMS reminder notifications for scheduled services'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Get all users who should receive notifications
        users = CustomUser.objects.filter(is_active=True)
        
        if not users.exists():
            self.stdout.write(
                self.style.WARNING('No active users found to send notifications to.')
            )
            return

        # Find PMS records scheduled for today, tomorrow, and day after tomorrow
        notifications_created = 0
        
        for days_ahead in [0, 1, 2]:  # Today, tomorrow, day after tomorrow
            target_date = today + timedelta(days=days_ahead)
            
            # Find scheduled PMS records for this date
            scheduled_pms = PMS.objects.filter(
                scheduled_date=target_date,
                status='Scheduled'
            )
            
            for pms in scheduled_pms:
                # Determine notification details based on days ahead
                if days_ahead == 0:
                    title = f"PMS Due Today: {pms.vehicle.plate_number}"
                    message = f"The PMS for {pms.vehicle.plate_number} ({pms.vehicle.brand} {pms.vehicle.model}) is scheduled for today ({target_date.strftime('%B %d, %Y')}). Please ensure the vehicle is ready for service."
                    priority = 'urgent'
                elif days_ahead == 1:
                    title = f"PMS Tomorrow: {pms.vehicle.plate_number}"
                    message = f"The PMS for {pms.vehicle.plate_number} ({pms.vehicle.brand} {pms.vehicle.model}) is scheduled for tomorrow ({target_date.strftime('%B %d, %Y')}). Please prepare the vehicle for service."
                    priority = 'high'
                else:  # days_ahead == 2
                    title = f"PMS in 2 Days: {pms.vehicle.plate_number}"
                    message = f"The PMS for {pms.vehicle.plate_number} ({pms.vehicle.brand} {pms.vehicle.model}) is scheduled in 2 days ({target_date.strftime('%B %d, %Y')}). Please plan accordingly."
                    priority = 'medium'
                
                # Create notifications for all users
                for user in users:
                    # Check if notification already exists to avoid duplicates
                    existing_notification = Notification.objects.filter(
                        user=user,
                        notification_type='pms_reminder',
                        title=title,
                        related_object_id=pms.id,
                        related_object_type='PMS',
                        created_at__date=today
                    ).exists()
                    
                    if not existing_notification:
                        Notification.objects.create(
                            user=user,
                            notification_type='pms_reminder',
                            title=title,
                            message=message,
                            priority=priority,
                            related_object_id=pms.id,
                            related_object_type='PMS'
                        )
                        notifications_created += 1
                        self.stdout.write(
                            f'Created notification for {user.username}: {title}'
                        )

        # Also check for overdue PMS records
        overdue_pms = PMS.objects.filter(
            scheduled_date__lt=today,
            status='Scheduled'
        )
        
        for pms in overdue_pms:
            days_overdue = (today - pms.scheduled_date).days
            
            title = f"PMS Overdue: {pms.vehicle.plate_number}"
            message = f"The PMS for {pms.vehicle.plate_number} ({pms.vehicle.brand} {pms.vehicle.model}) is {days_overdue} day(s) overdue (scheduled for {pms.scheduled_date.strftime('%B %d, %Y')}). Please reschedule immediately."
            priority = 'urgent'
            
            for user in users:
                # Check if overdue notification already exists today
                existing_notification = Notification.objects.filter(
                    user=user,
                    notification_type='pms_overdue',
                    title=title,
                    related_object_id=pms.id,
                    related_object_type='PMS',
                    created_at__date=today
                ).exists()
                
                if not existing_notification:
                    Notification.objects.create(
                        user=user,
                        notification_type='pms_overdue',
                        title=title,
                        message=message,
                        priority=priority,
                        related_object_id=pms.id,
                        related_object_type='PMS'
                    )
                    notifications_created += 1
                    self.stdout.write(
                        f'Created overdue notification for {user.username}: {title}'
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {notifications_created} PMS notifications'
            )
        )
