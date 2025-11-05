from django.utils import timezone
from core.models import Notification

def notifications(request):
    """Context processor to make notification data available on all pages"""
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-created_at')[:10]
        
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return {
            'unread_notifications': unread_notifications,
            'unread_count': unread_count,
        }
    return {
        'unread_notifications': [],
        'unread_count': 0,
    }
