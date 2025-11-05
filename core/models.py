from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from decimal import Decimal


class CustomUser(AbstractUser):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
    
    # Vehicle Permissions
    can_view_vehicles = models.BooleanField(default=False)
    can_add_vehicles = models.BooleanField(default=False)
    can_edit_vehicles = models.BooleanField(default=False)
    can_delete_vehicles = models.BooleanField(default=False)
    
    # Repair Permissions
    can_view_repairs = models.BooleanField(default=False)
    can_add_repairs = models.BooleanField(default=False)
    can_edit_repairs = models.BooleanField(default=False)
    can_delete_repairs = models.BooleanField(default=False)
    can_complete_repairs = models.BooleanField(default=False)
    
    # PMS Permissions
    can_view_pms = models.BooleanField(default=False)
    can_add_pms = models.BooleanField(default=False)
    can_edit_pms = models.BooleanField(default=False)
    can_delete_pms = models.BooleanField(default=False)
    can_complete_pms = models.BooleanField(default=False)
    
    # Inspection Permissions
    can_view_inspections = models.BooleanField(default=False)
    can_add_inspections = models.BooleanField(default=False)
    can_edit_inspections = models.BooleanField(default=False)
    can_delete_inspections = models.BooleanField(default=False)
    can_approve_inspections = models.BooleanField(default=False)
    
    # User Management Permissions
    can_view_users = models.BooleanField(default=False)
    can_add_users = models.BooleanField(default=False)
    can_edit_users = models.BooleanField(default=False)
    can_delete_users = models.BooleanField(default=False)
    
    # Division Management Permissions
    can_view_divisions = models.BooleanField(default=False)
    can_add_divisions = models.BooleanField(default=False)
    can_edit_divisions = models.BooleanField(default=False)
    can_delete_divisions = models.BooleanField(default=False)
    
    # Driver Management Permissions
    can_view_drivers = models.BooleanField(default=False)
    can_add_drivers = models.BooleanField(default=False)
    can_edit_drivers = models.BooleanField(default=False)
    can_delete_drivers = models.BooleanField(default=False)
    
    # Repair Shop Management Permissions
    can_view_repair_shops = models.BooleanField(default=False)
    can_add_repair_shops = models.BooleanField(default=False)
    can_edit_repair_shops = models.BooleanField(default=False)
    can_delete_repair_shops = models.BooleanField(default=False)
    
    # System Permissions
    can_view_reports = models.BooleanField(default=False)
    can_view_operational_status = models.BooleanField(default=False)
    can_view_activity_logs = models.BooleanField(default=False)
    can_view_admin_dashboard = models.BooleanField(default=False)
    can_view_system_manual = models.BooleanField(default=False)
    can_view_notifications = models.BooleanField(default=False)
    can_mark_notifications_read = models.BooleanField(default=False)
    
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
        return f"{self.get_full_name()} ({self.username})"
    
    def has_admin_access(self):
        """Check if user has admin dashboard access"""
        return self.can_view_admin_dashboard
    
    def has_fleet_manager_access(self):
        """Check if user has fleet manager level access (can manage vehicles, repairs, PMS)"""
        return (self.can_view_vehicles or self.can_view_repairs or self.can_view_pms or 
                self.can_view_inspections or self.can_view_users)
    
    def get_permission_summary(self):
        """Get a summary of user's permissions"""
        permissions = []
        if self.can_view_admin_dashboard:
            permissions.append("Admin Dashboard")
        if self.can_view_users:
            permissions.append("User Management")
        if self.can_view_vehicles:
            permissions.append("Vehicle Management")
        if self.can_view_repairs:
            permissions.append("Repair Management")
        if self.can_view_pms:
            permissions.append("PMS Management")
        if self.can_view_inspections:
            permissions.append("Inspection Management")
        if self.can_view_reports:
            permissions.append("Reports")
        return ", ".join(permissions) if permissions else "No permissions"
    
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
        ('For Disposal', 'For Disposal'),
    ]
    
    VEHICLE_TYPE_CHOICES = [
        ('SEDAN', 'SEDAN'),
        ('SUV', 'SUV'),
        ('TRUCK', 'TRUCK'),
        ('PICK UP', 'PICK UP'),
        ('MOTORCYCLE', 'MOTORCYCLE'),
        ('CLOSE VAN', 'CLOSE VAN'),
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
    current_market_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='Current Market Value')
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Serviceable')
    status_changed_at = models.DateTimeField(null=True, blank=True, verbose_name='Status Changed At')
    status_changed_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicle_status_changes', verbose_name='Status Changed By')
    status_change_reason = models.TextField(blank=True, verbose_name='Status Change Reason')
    date_acquired = models.DateField()
    current_mileage = models.IntegerField(default=0)
    photos = models.JSONField(default=list, blank=True, help_text="List of vehicle photo file paths")
    registration_documents = models.JSONField(default=list, blank=True, help_text="List of registration document file paths")
    # RFID and Fleet Card Information
    rfid_autosweep_number = models.CharField(max_length=100, blank=True, verbose_name='Autosweep RFID Number')
    rfid_easytrip_number = models.CharField(max_length=100, blank=True, verbose_name='Easytrip RFID Number')
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
        """Calculate total repair costs including parts and labor for all completed repairs"""
        total = Decimal('0')
        for repair in self.repairs.filter(status='Completed'):
            total += repair.total_cost
        return total
    
    @property
    def disposal_threshold(self):
        """Calculate the disposal threshold: current_market_value / 2"""
        if not self.current_market_value or self.current_market_value <= 0:
            return None
        threshold = self.current_market_value / Decimal('2')
        return threshold
    
    @property
    def is_for_disposal(self):
        """Check if vehicle should be marked for disposal based on repair costs"""
        threshold = self.disposal_threshold
        if threshold is None:
            return False
        return self.total_repair_costs >= threshold
    
    def check_and_mark_for_disposal(self, user=None):
        """Check if vehicle exceeds threshold and automatically mark/unmark for disposal if needed"""
        # Refresh from DB to get latest repair costs
        self.refresh_from_db()
        
        threshold = self.disposal_threshold
        if threshold is None:
            return False
        
        total_costs = self.total_repair_costs
        is_for_disposal = total_costs >= threshold
        
        # Mark for disposal if costs exceed threshold
        if is_for_disposal and self.status != 'For Disposal':
            reason = f'Vehicle marked for disposal: Total repair costs ({total_costs:.2f}) exceed half of current market value (threshold: {threshold:.2f})'
            self.update_status('For Disposal', user=user, reason=reason, auto_update=True)
            return True
        
        # Unmark from disposal if costs drop below threshold
        if not is_for_disposal and self.status == 'For Disposal':
            # Check if vehicle has ongoing repairs
            ongoing_repairs = self.repairs.filter(status='Ongoing').exists()
            new_status = 'Under Repair' if ongoing_repairs else 'Serviceable'
            reason = f'Vehicle unmarked from disposal: Total repair costs ({total_costs:.2f}) are below threshold ({threshold:.2f})'
            self.update_status(new_status, user=user, reason=reason, auto_update=True)
            return True
        
        return False
    
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
    
    # Inspection reports
    pre_inspection = models.ForeignKey('PreInspectionReport', on_delete=models.CASCADE, related_name='repairs', null=True, blank=True)
    post_inspection = models.ForeignKey('PostInspectionReport', on_delete=models.SET_NULL, null=True, blank=True, related_name='repairs')
    
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
        # Enforce business rules
        # Skip PMS validation if skip_pms_validation is True
        # This allows repairs created from PMS to share the same pre_inspection
        skip_pms_validation = kwargs.pop('skip_pms_validation', False)
        if skip_pms_validation:
            self._validate_inspection_requirements_skip_pms()
        else:
            self._validate_inspection_requirements()
        
        # Store old status and cost to check if we need to re-calculate disposal status
        old_status = None
        old_cost = None
        if self.pk:
            try:
                old_repair = self.__class__.objects.get(pk=self.pk)
                old_status = old_repair.status
                old_cost = old_repair.cost + (old_repair.labor_cost or 0)
            except self.__class__.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Check if vehicle should be marked/unmarked for disposal
        # This happens when:
        # 1. A repair is marked as Completed
        # 2. A completed repair's cost is updated
        # 3. A repair is changed from Completed to Ongoing (reduces total costs)
        should_recheck_disposal = False
        current_cost = self.total_cost
        
        if self.status == 'Completed':
            # Always recheck when repair is completed or cost changes
            should_recheck_disposal = True
        elif old_status == 'Completed':
            # Repair was completed before - check if cost changed or status changed to Ongoing
            if old_cost != current_cost or self.status != 'Completed':
                should_recheck_disposal = True
        
        if should_recheck_disposal and self.vehicle.current_market_value:
            # Refresh vehicle from DB to get latest repair costs
            self.vehicle.refresh_from_db()
            self.vehicle.check_and_mark_for_disposal(user=None)
        
        # Check if status changed to Completed
        if self.status == 'Completed' and old_status != 'Completed':
            # Refresh vehicle from DB to get current status
            self.vehicle.refresh_from_db()
            
            # Check if there are any other ongoing repairs or PMS for this vehicle
            ongoing_repairs = self.vehicle.repairs.filter(status='Ongoing').exclude(id=self.id).exists()
            ongoing_pms = self.vehicle.pms_records.filter(status='In Progress').exists()
            
            # Only set to serviceable if:
            # 1. No ongoing repairs or PMS
            # 2. Vehicle is not marked for disposal
            # 3. Vehicle is currently Under Repair or Unserviceable (could be set to serviceable)
            if not ongoing_repairs and not ongoing_pms and self.vehicle.status != 'For Disposal':
                # Set vehicle to serviceable when all maintenance is completed
                self.vehicle.update_status(
                    'Serviceable', 
                    reason=f'Repair completed for vehicle {self.vehicle.plate_number}',
                    auto_update=True
                )
        elif old_status == 'Completed' and self.status != 'Completed':
            # Repair was un-completed, recheck disposal status as costs have decreased
            if self.vehicle.current_market_value:
                self.vehicle.refresh_from_db()
                self.vehicle.check_and_mark_for_disposal(user=None)
        
        elif self.status == 'Ongoing' and self.vehicle.status == 'Serviceable':
            # Set vehicle to under repair when repair starts
            self.vehicle.update_status(
                'Under Repair',
                reason=f'Repair started for vehicle {self.vehicle.plate_number}',
                auto_update=True
            )
    
    def _validate_inspection_requirements_skip_pms(self):
        """Validate inspection requirements except PMS usage checks (for repairs created from PMS)"""
        from django.core.exceptions import ValidationError
        
        # Rule 1: Cannot create repair without approved pre-inspection
        if not self.pk and not self.pre_inspection:
            raise ValidationError(
                "A repair cannot be created without an approved pre-inspection report. "
                "Please create and approve a pre-inspection report first."
            )
        
        # Rule 2: Cannot mark as completed without post-inspection
        if self.status == 'Completed' and not self.post_inspection:
            raise ValidationError(
                "A repair cannot be marked as completed without a post-inspection report. "
                "Please create and approve a post-inspection report first."
            )
        
        # Rule 3: Pre-inspection must be approved
        if self.pre_inspection and not self.pre_inspection.is_approved:
            raise ValidationError(
                "The pre-inspection report must be approved before creating a repair. "
                "Please approve the pre-inspection report first."
            )
        
        # Rule 4: Post-inspection must be approved only when marking repair as completed
        if self.status == 'Completed' and self.post_inspection and not self.post_inspection.is_approved:
            raise ValidationError(
                "The post-inspection report must be approved before marking repair as completed. "
                "Please approve the post-inspection report first."
            )
        
        # Rule 5: Pre-inspection vehicle must match repair vehicle
        if self.pre_inspection and self.vehicle:
            if self.pre_inspection.vehicle != self.vehicle:
                raise ValidationError(
                    f"The pre-inspection report is for vehicle {self.pre_inspection.vehicle.plate_number}, "
                    f"but this repair is for vehicle {self.vehicle.plate_number}. "
                    "The pre-inspection report must be for the same vehicle as the repair."
                )
        
        # Rule 6: Post-inspection vehicle must match repair vehicle
        if self.post_inspection and self.vehicle:
            if self.post_inspection.vehicle != self.vehicle:
                raise ValidationError(
                    f"The post-inspection report is for vehicle {self.post_inspection.vehicle.plate_number}, "
                    f"but this repair is for vehicle {self.vehicle.plate_number}. "
                    "The post-inspection report must be for the same vehicle as the repair."
                )
        
        # Rule 7: Check for other repairs using this pre_inspection (but skip PMS check)
        if self.pre_inspection:
            existing_repair = Repair.objects.filter(pre_inspection=self.pre_inspection).exclude(pk=self.pk if self.pk else None).first()
            if existing_repair:
                raise ValidationError(
                    f"This pre-inspection report is already used by repair record for vehicle {existing_repair.vehicle.plate_number}. "
                    "Each pre-inspection report can only be used once."
                )
        
        # Rule 8: Check for other repairs using this post_inspection (but skip PMS check)
        if self.post_inspection:
            existing_repair = Repair.objects.filter(post_inspection=self.post_inspection).exclude(pk=self.pk if self.pk else None).first()
            if existing_repair:
                raise ValidationError(
                    f"This post-inspection report is already used by repair record for vehicle {existing_repair.vehicle.plate_number}. "
                    "Each post-inspection report can only be used once."
                )
    
    def _validate_inspection_requirements(self):
        """Validate inspection requirements based on business rules"""
        from django.core.exceptions import ValidationError
        
        # Rule 1: Cannot create repair without approved pre-inspection
        if not self.pk and not self.pre_inspection:
            raise ValidationError(
                "A repair cannot be created without an approved pre-inspection report. "
                "Please create and approve a pre-inspection report first."
            )
        
        # Rule 2: Cannot mark as completed without post-inspection
        if self.status == 'Completed' and not self.post_inspection:
            raise ValidationError(
                "A repair cannot be marked as completed without a post-inspection report. "
                "Please create and approve a post-inspection report first."
            )
        
        # Rule 3: Pre-inspection must be approved
        if self.pre_inspection and not self.pre_inspection.is_approved:
            raise ValidationError(
                "The pre-inspection report must be approved before creating a repair. "
                "Please approve the pre-inspection report first."
            )
        
        # Rule 4: Post-inspection must be approved only when marking repair as completed
        if self.status == 'Completed' and self.post_inspection and not self.post_inspection.is_approved:
            raise ValidationError(
                "The post-inspection report must be approved before marking repair as completed. "
                "Please approve the post-inspection report first."
            )
        
        # Rule 5: Pre-inspection vehicle must match repair vehicle
        if self.pre_inspection and self.vehicle:
            if self.pre_inspection.vehicle != self.vehicle:
                raise ValidationError(
                    f"The pre-inspection report is for vehicle {self.pre_inspection.vehicle.plate_number}, "
                    f"but this repair is for vehicle {self.vehicle.plate_number}. "
                    "The pre-inspection report must be for the same vehicle as the repair."
                )
        
        # Rule 6: Post-inspection vehicle must match repair vehicle
        if self.post_inspection and self.vehicle:
            if self.post_inspection.vehicle != self.vehicle:
                raise ValidationError(
                    f"The post-inspection report is for vehicle {self.post_inspection.vehicle.plate_number}, "
                    f"but this repair is for vehicle {self.vehicle.plate_number}. "
                    "The post-inspection report must be for the same vehicle as the repair."
                )
        
        # Rule 7: Pre-inspection can only be used once (by one repair or one PMS)
        # Exception: A repair created from a PMS can share the same pre_inspection as the PMS
        if self.pre_inspection:
            existing_repair = Repair.objects.filter(pre_inspection=self.pre_inspection).exclude(pk=self.pk if self.pk else None).first()
            
            # Check for PMS records using this pre_inspection
            # IMPORTANT: Only check for standalone PMS (not linked to any repair yet)
            # If a PMS is linked to a repair, that repair can share the pre_inspection
            existing_pms = PMS.objects.filter(
                pre_inspection=self.pre_inspection,
                repair__isnull=True  # Only standalone PMS (not linked to a repair)
            ).first()
            
            if existing_repair:
                raise ValidationError(
                    f"This pre-inspection report is already used by repair record for vehicle {existing_repair.vehicle.plate_number}. "
                    "Each pre-inspection report can only be used once."
                )
            
            if existing_pms:
                # Found a standalone PMS using this pre_inspection
                # This is only allowed if this repair will be linked to that PMS
                # But we can't check that during validation, so we need to skip this check
                # and rely on the view to handle it correctly
                # Actually, we should allow it if the repair is being created from a PMS
                # Since we can't know that during model validation, we'll skip this check
                # and let the view/form handle it
                raise ValidationError(
                    f"[REPAIR MODEL VALIDATION] This pre-inspection report is already used by PMS record for vehicle {existing_pms.vehicle.plate_number}. "
                    f"Existing PMS ID: {existing_pms.pk}, Current Repair ID: {self.pk}. Each pre-inspection report can only be used once. "
                    f"Note: If this repair is being created from a PMS, use skip_pms_validation=True."
                )
        
        # Rule 8: Post-inspection can only be used once (by one repair or one PMS)
        if self.post_inspection:
            existing_repair = Repair.objects.filter(post_inspection=self.post_inspection).exclude(pk=self.pk if self.pk else None).first()
            existing_pms = PMS.objects.filter(post_inspection=self.post_inspection).first()
            
            if existing_repair:
                raise ValidationError(
                    f"This post-inspection report is already used by repair record for vehicle {existing_repair.vehicle.plate_number}. "
                    "Each post-inspection report can only be used once."
                )
            
            if existing_pms:
                raise ValidationError(
                    f"This post-inspection report is already used by PMS record for vehicle {existing_pms.vehicle.plate_number}. "
                    "Each post-inspection report can only be used once."
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


class PreInspectionReport(models.Model):
    """Pre-inspection report before repair or PMS"""
    
    REPORT_TYPE_CHOICES = [
        ('repair', 'Repair'),
        ('pms', 'PMS'),
    ]
    
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('critical', 'Critical'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='pre_inspections')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES)
    inspection_date = models.DateTimeField(auto_now_add=True)
    inspected_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='pre_inspections')
    
    # Vehicle condition assessment
    engine_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    transmission_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    brakes_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    suspension_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    electrical_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    body_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    tires_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    lights_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    
    # Mileage and fuel
    current_mileage = models.IntegerField()
    fuel_level = models.CharField(max_length=20, choices=[
        ('full', 'Full'),
        ('three_quarters', '3/4'),
        ('half', '1/2'),
        ('quarter', '1/4'),
        ('empty', 'Empty'),
    ])
    
    # Issues found
    issues_found = models.TextField(blank=True, help_text="List all issues found during inspection")
    safety_concerns = models.TextField(blank=True, help_text="Any safety concerns identified")
    recommended_actions = models.TextField(blank=True, help_text="Recommended actions before proceeding")
    
    # Photos
    photos = models.JSONField(default=list, blank=True, help_text="List of photo file paths")
    
    # Driver report attachments (multiple)
    driver_report_attachments = models.JSONField(default=list, blank=True, help_text="List of driver report attachment file paths")
    
    # Approval
    approved_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_pre_inspections')
    approval_date = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Pre-Inspection: {self.vehicle.plate_number} - {self.get_report_type_display()} ({self.inspection_date.date()})"
    
    @property
    def overall_condition(self):
        """Calculate overall condition based on individual assessments"""
        conditions = [
            self.engine_condition,
            self.transmission_condition,
            self.brakes_condition,
            self.suspension_condition,
            self.electrical_condition,
            self.body_condition,
            self.tires_condition,
            self.lights_condition,
        ]
        
        condition_scores = {
            'excellent': 5,
            'good': 4,
            'fair': 3,
            'poor': 2,
            'critical': 1,
        }
        
        avg_score = sum(condition_scores[cond] for cond in conditions) / len(conditions)
        
        if avg_score >= 4.5:
            return 'excellent'
        elif avg_score >= 3.5:
            return 'good'
        elif avg_score >= 2.5:
            return 'fair'
        elif avg_score >= 1.5:
            return 'poor'
        else:
            return 'critical'
    
    @property
    def is_approved(self):
        return self.approved_by is not None and self.approval_date is not None
    
    class Meta:
        ordering = ['-inspection_date']
        verbose_name = 'Pre-Inspection Report'
        verbose_name_plural = 'Pre-Inspection Reports'


class PostInspectionReport(models.Model):
    """Post-inspection report after repair or PMS completion"""
    
    REPORT_TYPE_CHOICES = [
        ('repair', 'Repair'),
        ('pms', 'PMS'),
    ]
    
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('critical', 'Critical'),
    ]
    
    SATISFACTION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('satisfactory', 'Satisfactory'),
        ('poor', 'Poor'),
        ('unsatisfactory', 'Unsatisfactory'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='post_inspections')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES)
    inspection_date = models.DateTimeField(auto_now_add=True)
    inspected_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='post_inspections')
    
    # Link to pre-inspection report
    pre_inspection = models.ForeignKey(PreInspectionReport, on_delete=models.CASCADE, related_name='post_inspections')
    
    # Work completion assessment
    work_completed_satisfactorily = models.BooleanField(default=True)
    quality_of_work = models.CharField(max_length=15, choices=SATISFACTION_CHOICES)
    timeliness = models.CharField(max_length=15, choices=SATISFACTION_CHOICES)
    cleanliness = models.CharField(max_length=15, choices=SATISFACTION_CHOICES)
    
    # Post-work condition assessment
    engine_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    transmission_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    brakes_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    suspension_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    electrical_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    body_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    tires_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    lights_condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    
    # Test drive results
    test_drive_performed = models.BooleanField(default=True)
    test_drive_distance = models.IntegerField(default=0, help_text="Distance driven during test (km)")
    test_drive_notes = models.TextField(blank=True, help_text="Notes from test drive")
    
    # Issues and recommendations
    remaining_issues = models.TextField(blank=True, help_text="Any issues that remain unresolved")
    future_recommendations = models.TextField(blank=True, help_text="Recommendations for future maintenance")
    warranty_notes = models.TextField(blank=True, help_text="Warranty information if applicable")
    
    # Photos
    photos = models.JSONField(default=list, blank=True, help_text="List of photo file paths")
    
    # Replaced parts images attachment (multiple images)
    replaced_parts_images = models.JSONField(default=list, blank=True, null=True, help_text="List of replaced parts image file paths")
    
    def get_replaced_parts_images_list(self):
        """Safely get replaced_parts_images as a list"""
        if self.replaced_parts_images is None:
            return []
        if isinstance(self.replaced_parts_images, list):
            return self.replaced_parts_images
        # Try to parse if it's a string
        if isinstance(self.replaced_parts_images, str):
            try:
                import json
                parsed = json.loads(self.replaced_parts_images)
                return parsed if isinstance(parsed, list) else []
            except:
                return []
        return []
    
    # Final approval
    approved_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_post_inspections')
    approval_date = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Post-Inspection: {self.vehicle.plate_number} - {self.get_report_type_display()} ({self.inspection_date.date()})"
    
    @property
    def overall_condition(self):
        """Calculate overall condition based on individual assessments"""
        conditions = [
            self.engine_condition,
            self.transmission_condition,
            self.brakes_condition,
            self.suspension_condition,
            self.electrical_condition,
            self.body_condition,
            self.tires_condition,
            self.lights_condition,
        ]
        
        condition_scores = {
            'excellent': 5,
            'good': 4,
            'fair': 3,
            'poor': 2,
            'critical': 1,
        }
        
        avg_score = sum(condition_scores[cond] for cond in conditions) / len(conditions)
        
        if avg_score >= 4.5:
            return 'excellent'
        elif avg_score >= 3.5:
            return 'good'
        elif avg_score >= 2.5:
            return 'fair'
        elif avg_score >= 1.5:
            return 'poor'
        else:
            return 'critical'
    
    @property
    def is_approved(self):
        return self.approved_by is not None and self.approval_date is not None
    
    @property
    def condition_improvement(self):
        """Compare post-inspection condition with pre-inspection condition"""
        pre_condition = self.pre_inspection.overall_condition
        post_condition = self.overall_condition
        
        condition_scores = {
            'excellent': 5,
            'good': 4,
            'fair': 3,
            'poor': 2,
            'critical': 1,
        }
        
        pre_score = condition_scores[pre_condition]
        post_score = condition_scores[post_condition]
        
        if post_score > pre_score:
            return 'improved'
        elif post_score == pre_score:
            return 'maintained'
        else:
            return 'deteriorated'
    
    class Meta:
        ordering = ['-inspection_date']
        verbose_name = 'Post-Inspection Report'
        verbose_name_plural = 'Post-Inspection Reports'


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
    
    # Inspection reports
    pre_inspection = models.ForeignKey('PreInspectionReport', on_delete=models.CASCADE, related_name='pms_records', null=True, blank=True)
    post_inspection = models.ForeignKey('PostInspectionReport', on_delete=models.SET_NULL, null=True, blank=True, related_name='pms_records')
    
    # Link to repair record if parts were replaced during PMS
    repair = models.ForeignKey(Repair, on_delete=models.SET_NULL, null=True, blank=True, related_name='pms_records', verbose_name='Associated Repair')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.service_type} - {self.scheduled_date}"
    
    def save(self, *args, **kwargs):
        # Enforce business rules
        # Skip pre-inspection usage validation if skip_usage_validation is True
        # This allows form validation to handle it (form already checks this)
        skip_usage_validation = kwargs.pop('skip_usage_validation', False)
        if not skip_usage_validation:
            self._validate_inspection_requirements()
        else:
            # Still validate other requirements, just not the usage checks
            self._validate_other_requirements()
        
        # Store old status to check if status changed
        old_status = None
        if self.pk:
            try:
                old_pms = self.__class__.objects.get(pk=self.pk)
                old_status = old_pms.status
            except self.__class__.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Auto-update vehicle status based on PMS status
        if self.status == 'In Progress' and self.vehicle.status == 'Serviceable':
            # Set vehicle to under repair when PMS starts
            self.vehicle.update_status(
                'Under Repair',
                reason=f'PMS in progress for vehicle {self.vehicle.plate_number}',
                auto_update=True
            )
        
        # Check if status changed to Completed
        elif self.status == 'Completed' and old_status != 'Completed':
            # Refresh vehicle from DB to get current status
            self.vehicle.refresh_from_db()
            
            # Check if there are ongoing repairs or PMS in progress
            ongoing_repairs = self.vehicle.repairs.filter(status='Ongoing').exists()
            ongoing_pms = self.vehicle.pms_records.filter(status='In Progress').exclude(id=self.id).exists()
            
            # Only set to serviceable if:
            # 1. No ongoing repairs or PMS
            # 2. Vehicle is not marked for disposal
            # 3. Vehicle is currently Under Repair or Unserviceable (could be set to serviceable)
            if not ongoing_repairs and not ongoing_pms and self.vehicle.status != 'For Disposal':
                # Set vehicle to serviceable when all maintenance is completed
                self.vehicle.update_status(
                    'Serviceable',
                    reason=f'PMS completed for vehicle {self.vehicle.plate_number}',
                    auto_update=True
                )
    
    def _validate_other_requirements(self):
        """Validate inspection requirements except usage checks (for form saves)"""
        from django.core.exceptions import ValidationError
        
        # Rule 1: Cannot create PMS without approved pre-inspection
        if not self.pk and not self.pre_inspection:
            raise ValidationError(
                "A PMS record cannot be created without an approved pre-inspection report. "
                "Please create and approve a pre-inspection report first."
            )
        
        # Rule 2: Cannot mark as completed without post-inspection
        if self.status == 'Completed' and not self.post_inspection:
            raise ValidationError(
                "A PMS record cannot be marked as completed without a post-inspection report. "
                "Please create and approve a post-inspection report first."
            )
        
        # Rule 3: Pre-inspection must be approved
        if self.pre_inspection and not self.pre_inspection.is_approved:
            raise ValidationError(
                "The pre-inspection report must be approved before creating a PMS record. "
                "Please approve the pre-inspection report first."
            )
        
        # Rule 4: Post-inspection must be approved only when marking PMS as completed
        if self.status == 'Completed' and self.post_inspection and not self.post_inspection.is_approved:
            raise ValidationError(
                "The post-inspection report must be approved before marking PMS as completed. "
                "Please approve the post-inspection report first."
            )
        
        # Rule 5: Pre-inspection vehicle must match PMS vehicle
        if self.pre_inspection and self.vehicle:
            if self.pre_inspection.vehicle != self.vehicle:
                raise ValidationError(
                    f"The pre-inspection report is for vehicle {self.pre_inspection.vehicle.plate_number}, "
                    f"but this PMS is for vehicle {self.vehicle.plate_number}. "
                    "The pre-inspection report must be for the same vehicle as the PMS."
                )
        
        # Rule 6: Post-inspection vehicle must match PMS vehicle
        if self.post_inspection and self.vehicle:
            if self.post_inspection.vehicle != self.vehicle:
                raise ValidationError(
                    f"The post-inspection report is for vehicle {self.post_inspection.vehicle.plate_number}, "
                    f"but this PMS is for vehicle {self.vehicle.plate_number}. "
                    "The post-inspection report must be for the same vehicle as the PMS."
                )
    
    def _validate_inspection_requirements(self):
        """Validate inspection requirements based on business rules"""
        from django.core.exceptions import ValidationError
        
        # First validate other requirements
        self._validate_other_requirements()
        
        # Rule 7: Check if pre-inspection is already used by another repair or PMS
        # Exclude current instance and repairs created from this PMS
        # NOTE: This validation is also done in the form, but we keep it here as a safety check
        # However, we must be careful to exclude the current instance to avoid false positives
        if self.pre_inspection:
            # Check for standalone repairs (not linked to PMS) using this pre_inspection
            standalone_repairs = Repair.objects.filter(
                pre_inspection=self.pre_inspection,
                pms_records__isnull=True
            )
            # Exclude repairs created from this PMS if it exists
            if self.pk and self.repair:
                standalone_repairs = standalone_repairs.exclude(pk=self.repair.pk)
            existing_repair = standalone_repairs.first()
            
            # Check for other PMS records using this pre_inspection
            # CRITICAL: Exclude current instance - without this, we'd find ourselves when saving
            pms_query = PMS.objects.filter(pre_inspection=self.pre_inspection)
            if self.pk:
                pms_query = pms_query.exclude(pk=self.pk)
            existing_pms = pms_query.first()
            
            if existing_repair:
                raise ValidationError(
                    f"This pre-inspection report is already used by repair record for vehicle {existing_repair.vehicle.plate_number}. "
                    "Each pre-inspection report can only be used once."
                )
            
            if existing_pms:
                # Final check: ensure we're not comparing against ourselves
                if existing_pms.pk != self.pk:
                    raise ValidationError(
                        f"[MODEL VALIDATION] This pre-inspection report is already used by PMS record for vehicle {existing_pms.vehicle.plate_number}. "
                        f"Existing PMS ID: {existing_pms.pk}, Current PMS ID: {self.pk}. Each pre-inspection report can only be used once."
                    )
        
        # Rule 8: Check if post-inspection is already used by another repair or PMS
        # Exclude current instance and repairs created from this PMS
        if self.post_inspection:
            # Check for standalone repairs (not linked to PMS) using this post_inspection
            standalone_repairs = Repair.objects.filter(
                post_inspection=self.post_inspection,
                pms_records__isnull=True
            )
            # Exclude repairs created from this PMS if it exists
            if self.pk and self.repair:
                standalone_repairs = standalone_repairs.exclude(pk=self.repair.pk)
            existing_repair = standalone_repairs.first()
            
            # Check for other PMS records using this post_inspection
            # CRITICAL: Exclude current instance
            pms_query = PMS.objects.filter(post_inspection=self.post_inspection)
            if self.pk:
                pms_query = pms_query.exclude(pk=self.pk)
            existing_pms = pms_query.first()
            
            if existing_repair:
                raise ValidationError(
                    f"This post-inspection report is already used by repair record for vehicle {existing_repair.vehicle.plate_number}. "
                    "Each post-inspection report can only be used once."
                )
            
            if existing_pms:
                # Final check: ensure we're not comparing against ourselves
                if existing_pms.pk != self.pk:
                    raise ValidationError(
                        f"[MODEL VALIDATION] This post-inspection report is already used by PMS record for vehicle {existing_pms.vehicle.plate_number}. "
                        f"Existing PMS ID: {existing_pms.pk}, Current PMS ID: {self.pk}. Each post-inspection report can only be used once."
                    )
    
    class Meta:
        verbose_name = 'Preventive Maintenance Service'
        verbose_name_plural = 'Preventive Maintenance Services'
        ordering = ['-scheduled_date', '-created_at']
