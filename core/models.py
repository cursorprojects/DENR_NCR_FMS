from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('fleet_manager', 'Fleet Manager'),
        ('encoder', 'Encoder/Staff'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='encoder')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
    
    # Override the related_name for groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='customuser',
    )
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def has_fleet_manager_access(self):
        return self.role in ['super_admin', 'fleet_manager']
    
    def has_admin_access(self):
        return self.role == 'super_admin'
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('login', 'Logged In'),
        ('logout', 'Logged Out'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_action_display()} {self.model_name}"
    
    class Meta:
        ordering = ['-timestamp']


class Division(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class Driver(models.Model):
    name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    def __str__(self):
        return self.name


class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('Serviceable', 'Serviceable'),
        ('Under Repair', 'Under Repair'),
        ('Unserviceable', 'Unserviceable'),
    ]
    
    RFID_TYPE_CHOICES = [
        ('Autosweep', 'Autosweep'),
        ('Easytrip', 'Easytrip'),
    ]
    
    VEHICLE_TYPE_CHOICES = [
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('Hatchback', 'Hatchback'),
        ('Coupe', 'Coupe'),
        ('Convertible', 'Convertible'),
        ('Pickup Truck', 'Pickup Truck'),
        ('Van', 'Van'),
        ('Minivan', 'Minivan'),
        ('Wagon', 'Wagon'),
        ('Sports Car', 'Sports Car'),
        ('Motorcycle', 'Motorcycle'),
        ('Bicycle', 'Bicycle'),
        ('Bus', 'Bus'),
        ('Ambulance', 'Ambulance'),
        ('Fire Truck', 'Fire Truck'),
        ('Police Car', 'Police Car'),
        ('Other', 'Other'),
    ]
    
    plate_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=100, choices=VEHICLE_TYPE_CHOICES)
    model = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    year = models.IntegerField(
        validators=[MinValueValidator(1900)]
    )
    engine_number = models.CharField(max_length=100, blank=True, verbose_name='Engine Number')
    chassis_number = models.CharField(max_length=100, blank=True, verbose_name='Chassis Number')
    color = models.CharField(max_length=50, blank=True, verbose_name='Color')
    acquisition_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='Acquisition Cost')
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Serviceable')
    status_changed_at = models.DateTimeField(null=True, blank=True, verbose_name='Status Changed At')
    status_changed_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicle_status_changes', verbose_name='Status Changed By')
    status_change_reason = models.TextField(blank=True, verbose_name='Status Change Reason')
    date_acquired = models.DateField()
    current_mileage = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    registration_document = models.FileField(upload_to='documents/', blank=True, null=True)
    # RFID and Fleet Card Information
    rfid_number = models.CharField(max_length=100, blank=True, verbose_name='RFID Number')
    rfid_type = models.CharField(max_length=20, choices=RFID_TYPE_CHOICES, blank=True, null=True, verbose_name='RFID Type')
    fleet_card_number = models.CharField(max_length=100, blank=True, verbose_name='Fleet Card Number')
    gas_station = models.CharField(max_length=200, blank=True, verbose_name='Gas Station')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.plate_number} - {self.brand} {self.model}"
    
    def update_status(self, new_status, user=None, reason='', auto_update=False):
        """Update vehicle status with tracking"""
        from django.utils import timezone
        
        old_status = self.status
        self.status = new_status
        self.status_changed_at = timezone.now()
        self.status_changed_by = user
        self.status_change_reason = reason
        
        # Save the vehicle
        self.save()
        
        # Create notification if not auto-update
        if not auto_update and user:
            self._create_status_change_notification(old_status, new_status, user, reason)
        
        return True
    
    def _create_status_change_notification(self, old_status, new_status, user, reason):
        """Create notification for status change"""
        try:
            Notification.objects.create(
                user=user,
                notification_type='vehicle_status',
                title=f'Vehicle Status Changed: {self.plate_number}',
                message=f'Vehicle {self.plate_number} status changed from {old_status} to {new_status}. Reason: {reason}',
                priority='medium',
                related_object_type='Vehicle',
                related_object_id=self.id
            )
        except Exception as e:
            # Log error but don't fail the status update
            print(f"Error creating status change notification: {e}")
    
    @property
    def total_repair_costs(self):
        return self.repairs.filter(status='Completed').aggregate(
            total=models.Sum('cost')
        )['total'] or 0
    
    class Meta:
        ordering = ['-created_at']


class RepairShop(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    contact_person = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class RepairPart(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Repair Part'
        verbose_name_plural = 'Repair Parts'


class Repair(models.Model):
    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Ongoing', 'Ongoing'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='repairs')
    date_of_repair = models.DateField()
    description = models.TextField()
    
    # Keeping old fields for backward compatibility (will be phased out)
    repairing_part = models.ForeignKey(RepairPart, on_delete=models.SET_NULL, null=True, blank=True, related_name='repairs')
    part_additional_info = models.TextField(blank=True, verbose_name='Additional Info')
    part_quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], verbose_name='Quantity')
    part_unit = models.CharField(max_length=50, blank=True, verbose_name='Unit of Measurement')
    
    DISPOSAL_CHOICES = [
        ('normal', 'Normal Disposal'),
        ('trade_in', 'Trade-In'),
        ('waste', 'Waste Material'),
    ]
    
    disposal_type = models.CharField(max_length=20, choices=DISPOSAL_CHOICES, default='normal', verbose_name='Disposal Type')
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], verbose_name='Labor Cost')
    repair_shop = models.ForeignKey(RepairShop, on_delete=models.SET_NULL, null=True, blank=True)
    technician = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ongoing')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.date_of_repair}"
    
    @property
    def total_cost(self):
        """Calculate total cost as sum of parts cost and labor cost"""
        parts_cost = self.cost or 0
        labor_cost = self.labor_cost or 0
        return parts_cost + labor_cost
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Auto-update vehicle status based on repair status
        if self.status == 'Completed':
            # Check if there are any other ongoing repairs for this vehicle
            ongoing_repairs = self.vehicle.repairs.filter(status='Ongoing').exclude(id=self.id)
            if not ongoing_repairs.exists() and self.vehicle.status == 'Under Repair':
                # No more ongoing repairs, set vehicle to serviceable
                self.vehicle.update_status(
                    'Serviceable', 
                    reason=f'All repairs completed for vehicle {self.vehicle.plate_number}',
                    auto_update=True
                )
        
        elif self.status == 'Ongoing' and self.vehicle.status == 'Serviceable':
            # Set vehicle to under repair when repair starts
            self.vehicle.update_status(
                'Under Repair',
                reason=f'Repair started for vehicle {self.vehicle.plate_number}',
                auto_update=True
            )
    
    class Meta:
        ordering = ['-date_of_repair', '-created_at']


class RepairPartItem(models.Model):
    """Model to store multiple parts replaced per repair"""
    repair = models.ForeignKey(Repair, on_delete=models.CASCADE, related_name='part_items')
    part = models.ForeignKey(RepairPart, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], verbose_name='Quantity')
    unit = models.CharField(max_length=50, blank=True, verbose_name='Unit')
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], verbose_name='Cost')
    additional_info = models.TextField(blank=True, verbose_name='Additional Info')
    disposal_type = models.CharField(max_length=20, choices=Repair.DISPOSAL_CHOICES, default='normal', verbose_name='Disposal Type')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.repair.vehicle.plate_number} - {self.part.name if self.part else 'Unknown'}"
    
    class Meta:
        ordering = ['-created_at']


class Notification(models.Model):
    """System notifications for users"""
    NOTIFICATION_TYPES = [
        ('pms_reminder', 'PMS Reminder'),
        ('pms_overdue', 'PMS Overdue'),
        ('repair_completed', 'Repair Completed'),
        ('vehicle_status', 'Vehicle Status Change'),
        ('general', 'General Notification'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_read = models.BooleanField(default=False)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'


class PMS(models.Model):
    """Preventive Maintenance Service"""
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Overdue', 'Overdue'),
        ('Cancelled', 'Cancelled'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='pms_records')
    service_type = models.CharField(max_length=50, default='General Inspection', verbose_name='Service Type')
    scheduled_date = models.DateField(verbose_name='Scheduled Date')
    completed_date = models.DateField(null=True, blank=True, verbose_name='Completed Date')
    mileage_at_service = models.IntegerField(default=0, verbose_name='Mileage at Service')
    next_service_mileage = models.IntegerField(null=True, blank=True, verbose_name='Next Service Mileage')
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], verbose_name='Service Cost')
    provider = models.CharField(max_length=200, blank=True, verbose_name='Service Provider')
    technician = models.CharField(max_length=200, blank=True, verbose_name='Technician')
    description = models.TextField(blank=True, verbose_name='Service Description')
    notes = models.TextField(blank=True, verbose_name='Additional Notes')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled', verbose_name='Status')
    # Link to repair record if parts were replaced during PMS
    repair = models.ForeignKey(Repair, on_delete=models.SET_NULL, null=True, blank=True, related_name='pms_records', verbose_name='Associated Repair')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.service_type} - {self.scheduled_date}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Auto-update vehicle status based on PMS status
        if self.status == 'In Progress' and self.vehicle.status == 'Serviceable':
            # Set vehicle to under repair when PMS starts
            self.vehicle.update_status(
                'Under Repair',
                reason=f'PMS in progress for vehicle {self.vehicle.plate_number}',
                auto_update=True
            )
        
        elif self.status == 'Completed':
            # Check if there are ongoing repairs or PMS in progress
            ongoing_repairs = self.vehicle.repairs.filter(status='Ongoing').exists()
            ongoing_pms = self.vehicle.pms_records.filter(status='In Progress').exclude(id=self.id).exists()
            
            if not ongoing_repairs and not ongoing_pms and self.vehicle.status == 'Under Repair':
                # No ongoing maintenance, set vehicle to serviceable
                self.vehicle.update_status(
                    'Serviceable',
                    reason=f'PMS completed for vehicle {self.vehicle.plate_number}',
                    auto_update=True
                )
    
    class Meta:
        verbose_name = 'Preventive Maintenance Service'
        verbose_name_plural = 'Preventive Maintenance Services'
        ordering = ['-scheduled_date', '-created_at']
