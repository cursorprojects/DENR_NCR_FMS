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


class Department(models.Model):
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
    
    plate_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    year = models.IntegerField(
        validators=[MinValueValidator(1900)]
    )
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Serviceable')
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
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # If repair status is completed, check if vehicle should be serviceable
        if self.status == 'Completed':
            ongoing_repairs = self.vehicle.repairs.filter(status='Ongoing').exists()
            if not ongoing_repairs and self.vehicle.status == 'Under Repair':
                self.vehicle.status = 'Serviceable'
                self.vehicle.save()
        
        # If repair status is ongoing, set vehicle to under repair
        if self.status == 'Ongoing' and self.vehicle.status == 'Serviceable':
            self.vehicle.status = 'Under Repair'
            self.vehicle.save()
    
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
        verbose_name = 'Repair Part Item'
        verbose_name_plural = 'Repair Part Items'
