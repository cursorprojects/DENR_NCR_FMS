from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # User Management URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('activity-logs/', views.activity_logs, name='activity_logs'),
    
    # Division Management URLs
    path('divisions/', views.division_list, name='division_list'),
    path('divisions/add/', views.division_create, name='division_create'),
    path('divisions/<int:pk>/edit/', views.division_edit, name='division_edit'),
    path('divisions/<int:pk>/delete/', views.division_delete, name='division_delete'),
    
    # Driver Management URLs
    path('drivers/', views.driver_list, name='driver_list'),
    path('drivers/add/', views.driver_create, name='driver_create'),
    path('drivers/<int:pk>/edit/', views.driver_edit, name='driver_edit'),
    path('drivers/<int:pk>/delete/', views.driver_delete, name='driver_delete'),
    
    # Repair Shop Management URLs
    path('repair-shops/', views.repairshop_list, name='repairshop_list'),
    path('repair-shops/add/', views.repairshop_create, name='repairshop_create'),
    path('repair-shops/<int:pk>/edit/', views.repairshop_edit, name='repairshop_edit'),
    path('repair-shops/<int:pk>/delete/', views.repairshop_delete, name='repairshop_delete'),
    
    # Vehicle URLs
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/add/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),
    path('vehicles/<int:pk>/status-change/', views.vehicle_status_change, name='vehicle_status_change'),
    
    # Repair URLs
    path('repairs/', views.repair_list, name='repair_list'),
    path('repairs/<int:pk>/', views.repair_detail, name='repair_detail'),
    path('repairs/add/', views.repair_create, name='repair_create'),
    path('repairs/<int:pk>/edit/', views.repair_edit, name='repair_edit'),
    path('repairs/<int:pk>/delete/', views.repair_delete, name='repair_delete'),
    path('repairs/<int:pk>/complete/', views.repair_complete, name='repair_complete'),
    
    # PMS URLs
    path('pms/', views.pms_list, name='pms_list'),
    path('pms/<int:pk>/', views.pms_detail, name='pms_detail'),
    path('pms/add/', views.pms_create, name='pms_create'),
    path('pms/<int:pk>/edit/', views.pms_edit, name='pms_edit'),
    path('pms/<int:pk>/delete/', views.pms_delete, name='pms_delete'),
    path('pms/<int:pk>/complete/', views.pms_complete, name='pms_complete'),
    
    # Operational Status
    path('status/', views.operational_status, name='operational_status'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # System Manual
    path('manual/', views.system_manual, name='system_manual'),
    
    # Inspection Report URLs
    # Pre-Inspection Reports
    path('pre-inspections/', views.pre_inspection_list, name='pre_inspection_list'),
    path('pre-inspections/add/', views.pre_inspection_create, name='pre_inspection_create'),
    path('pre-inspections/<int:pk>/', views.pre_inspection_detail, name='pre_inspection_detail'),
    path('pre-inspections/<int:pk>/edit/', views.pre_inspection_edit, name='pre_inspection_edit'),
    path('pre-inspections/<int:pk>/approve/', views.pre_inspection_approve, name='pre_inspection_approve'),
    path('pre-inspections/<int:pk>/delete/', views.pre_inspection_delete, name='pre_inspection_delete'),
    
    # Post-Inspection Reports
    path('post-inspections/', views.post_inspection_list, name='post_inspection_list'),
    path('post-inspections/add/', views.post_inspection_create, name='post_inspection_create'),
    path('post-inspections/<int:pk>/', views.post_inspection_detail, name='post_inspection_detail'),
    path('post-inspections/<int:pk>/edit/', views.post_inspection_edit, name='post_inspection_edit'),
    path('post-inspections/<int:pk>/approve/', views.post_inspection_approve, name='post_inspection_approve'),
    path('post-inspections/<int:pk>/delete/', views.post_inspection_delete, name='post_inspection_delete'),
    
    # AJAX endpoints
    path('api/pre-inspections-by-vehicle/', views.get_pre_inspections_by_vehicle, name='get_pre_inspections_by_vehicle'),
]
