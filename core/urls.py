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
    
    # Department Management URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    
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
    
    # Repair URLs
    path('repairs/', views.repair_list, name='repair_list'),
    path('repairs/<int:pk>/', views.repair_detail, name='repair_detail'),
    path('repairs/add/', views.repair_create, name='repair_create'),
    path('repairs/<int:pk>/edit/', views.repair_edit, name='repair_edit'),
    path('repairs/<int:pk>/delete/', views.repair_delete, name='repair_delete'),
    
    # PMS URLs
    path('pms/', views.pms_list, name='pms_list'),
    path('pms/<int:pk>/', views.pms_detail, name='pms_detail'),
    path('pms/add/', views.pms_create, name='pms_create'),
    path('pms/<int:pk>/edit/', views.pms_edit, name='pms_edit'),
    path('pms/<int:pk>/delete/', views.pms_delete, name='pms_delete'),
    
    # Operational Status
    path('status/', views.operational_status, name='operational_status'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
]
