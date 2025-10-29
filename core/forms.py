from django import forms
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory
from .models import Vehicle, Repair, Driver, Division, RepairShop, RepairPart, RepairPartItem, PMS, PreInspectionReport, PostInspectionReport

User = get_user_model()


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'plate_number', 'vehicle_type', 'model', 'brand', 'year',
            'engine_number', 'chassis_number', 'color', 'acquisition_cost',
            'division', 'assigned_driver', 'status', 'date_acquired',
            'current_mileage', 'rfid_number', 'rfid_type', 'fleet_card_number',
            'gas_station', 'photo', 'registration_document', 'notes'
        ]
        widgets = {
            'plate_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'engine_number': forms.TextInput(attrs={'class': 'form-control'}),
            'chassis_number': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'acquisition_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'division': forms.Select(attrs={'class': 'form-control'}),
            'assigned_driver': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'date_acquired': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'current_mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'rfid_number': forms.TextInput(attrs={'class': 'form-control'}),
            'rfid_type': forms.Select(attrs={'class': 'form-control'}),
            'fleet_card_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gas_station': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'registration_document': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class RepairPartItemForm(forms.ModelForm):
    UNIT_CHOICES = [
        ('', 'Select unit...'),
        ('pcs', 'Pieces (pcs)'),
        ('set', 'Set'),
        ('pair', 'Pair'),
        ('liter', 'Liter'),
        ('gallon', 'Gallon'),
        ('kg', 'Kilogram (kg)'),
        ('g', 'Gram (g)'),
        ('m', 'Meter (m)'),
        ('cm', 'Centimeter (cm)'),
        ('mm', 'Millimeter (mm)'),
        ('sq m', 'Square Meter'),
        ('cu m', 'Cubic Meter'),
        ('box', 'Box'),
        ('bottle', 'Bottle'),
        ('can', 'Can'),
        ('sheet', 'Sheet'),
        ('roll', 'Roll'),
    ]
    
    unit = forms.ChoiceField(choices=UNIT_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = RepairPartItem
        fields = ['part', 'quantity', 'unit', 'cost', 'additional_info', 'disposal_type']
        widgets = {
            'part': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost': forms.TextInput(attrs={'class': 'form-control decimal-input'}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'disposal_type': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active repair parts
        self.fields['part'].queryset = RepairPart.objects.filter(is_active=True)
        self.fields['part'].empty_label = "Select a part..."
        self.fields['part'].label = "Part"
        
        # If editing, populate the unit field
        if self.instance and self.instance.pk and self.instance.unit:
            self.fields['unit'].initial = self.instance.unit


# Create formset factory for Repair
RepairPartItemFormSet = inlineformset_factory(
    Repair, 
    RepairPartItem, 
    form=RepairPartItemForm,
    extra=0,  # No extra forms by default
    can_delete=True,
    can_delete_extra=False
)

# Create formset factory for PMS (same as Repair - both use RepairPartItem)
PMSRepairPartItemFormSet = inlineformset_factory(
    Repair, 
    RepairPartItem, 
    form=RepairPartItemForm,
    extra=1,  # Start with 1 empty form for convenience
    can_delete=True,
    can_delete_extra=False
)


class RepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = [
            'vehicle', 'date_of_repair', 'description',
            'cost', 'labor_cost', 'repair_shop', 'technician', 'status', 'pre_inspection'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'date_of_repair': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'labor_cost': forms.TextInput(attrs={'class': 'form-control decimal-input'}),
            'repair_shop': forms.Select(attrs={'class': 'form-control'}),
            'technician': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'pre_inspection': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active repair shops in the dropdown
        self.fields['repair_shop'].queryset = RepairShop.objects.filter(is_active=True)
        self.fields['repair_shop'].empty_label = "Select a repair shop..."
        
        # Filter pre-inspections to only show approved ones for repairs
        self.fields['pre_inspection'].queryset = PreInspectionReport.objects.filter(
            report_type='repair',
            approved_by__isnull=False
        ).order_by('-inspection_date')
        self.fields['pre_inspection'].empty_label = "Select an approved pre-inspection report..."
        self.fields['pre_inspection'].required = True
        
        # Add help text
        self.fields['pre_inspection'].help_text = "Required: Select an approved pre-inspection report for repairs"
        
        # Disable status field if repair is completed or if no post-inspection exists
        if self.instance.pk:
            if self.instance.status == 'Completed':
                self.fields['status'].widget.attrs['disabled'] = True
                self.fields['status'].help_text = "Status cannot be changed once marked as completed. Use post-inspection workflow."
            elif self.instance.status == 'Ongoing' and not self.instance.post_inspection:
                # Allow changing from Ongoing to Completed only if post-inspection exists
                status_choices = list(self.fields['status'].choices)
                # Remove 'Completed' option if no post-inspection
                self.fields['status'].choices = [(k, v) for k, v in status_choices if k != 'Completed']
                self.fields['status'].help_text = "Cannot mark as completed without post-inspection report."
    
    def clean(self):
        cleaned_data = super().clean()
        pre_inspection = cleaned_data.get('pre_inspection')
        status = cleaned_data.get('status')
        
        # Additional validation
        if pre_inspection and not pre_inspection.is_approved:
            raise forms.ValidationError(
                "The selected pre-inspection report must be approved before creating a repair."
            )
        
        if status == 'Completed' and not self.instance.post_inspection:
            raise forms.ValidationError(
                "Cannot mark repair as completed without a post-inspection report. "
                "Please create and approve a post-inspection report first."
            )
        
        return cleaned_data


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name', 'license_number', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PMSForm(forms.ModelForm):
    # Make provider a dropdown of repair shops
    repair_shop = forms.ModelChoiceField(
        queryset=RepairShop.objects.none(),  # Will be set in __init__
        required=False,
        empty_label='Select a repair shop',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Service Provider'
    )
    
    class Meta:
        model = PMS
        fields = [
            'vehicle', 'service_type', 'scheduled_date', 'completed_date',
            'mileage_at_service', 'next_service_mileage', 'cost',
            'provider', 'technician', 'description', 'notes', 'status', 'pre_inspection'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'service_type': forms.HiddenInput(),  # Always set to 'General Inspection'
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'completed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mileage_at_service': forms.NumberInput(attrs={'class': 'form-control'}),
            'next_service_mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost': forms.TextInput(attrs={'class': 'form-control decimal-input'}),
            'provider': forms.HiddenInput(),  # Will be populated by repair_shop
            'technician': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'pre_inspection': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set the queryset for repair_shop field
        self.fields['repair_shop'].queryset = RepairShop.objects.filter(is_active=True)
        
        # Always set service type to 'General Inspection'
        self.fields['service_type'].initial = 'General Inspection'
        self.fields['service_type'].required = False
        
        # Filter pre-inspections to only show approved ones for PMS
        self.fields['pre_inspection'].queryset = PreInspectionReport.objects.filter(
            report_type='pms',
            approved_by__isnull=False
        ).order_by('-inspection_date')
        self.fields['pre_inspection'].empty_label = "Select an approved pre-inspection report..."
        self.fields['pre_inspection'].required = True
        
        # Add help text
        self.fields['pre_inspection'].help_text = "Required: Select an approved pre-inspection report for PMS"
        
        # Disable status field if PMS is completed or if no post-inspection exists
        if self.instance.pk:
            if self.instance.status == 'Completed':
                self.fields['status'].widget.attrs['disabled'] = True
                self.fields['status'].help_text = "Status cannot be changed once marked as completed. Use post-inspection workflow."
            elif self.instance.status == 'In Progress' and not self.instance.post_inspection:
                # Allow changing from In Progress to Completed only if post-inspection exists
                status_choices = list(self.fields['status'].choices)
                # Remove 'Completed' option if no post-inspection
                self.fields['status'].choices = [(k, v) for k, v in status_choices if k != 'Completed']
                self.fields['status'].help_text = "Cannot mark as completed without post-inspection report."
        
        # If editing and there's a provider, try to find matching repair shop
        if self.instance.pk and self.instance.provider:
            try:
                repair_shop = RepairShop.objects.get(name=self.instance.provider)
                self.fields['repair_shop'].initial = repair_shop.id
            except (RepairShop.DoesNotExist, RepairShop.MultipleObjectsReturned):
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        pre_inspection = cleaned_data.get('pre_inspection')
        status = cleaned_data.get('status')
        
        # Additional validation
        if pre_inspection and not pre_inspection.is_approved:
            raise forms.ValidationError(
                "The selected pre-inspection report must be approved before creating a PMS record."
            )
        
        if status == 'Completed' and not self.instance.post_inspection:
            raise forms.ValidationError(
                "Cannot mark PMS as completed without a post-inspection report. "
                "Please create and approve a post-inspection report first."
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Save the repair shop name as provider
        repair_shop = self.cleaned_data.get('repair_shop')
        if repair_shop:
            instance.provider = repair_shop.name
        elif not instance.provider:  # If no repair shop selected, clear provider
            instance.provider = ''
        if commit:
            instance.save()
        return instance


class UserForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    
class UserForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'status', 'phone',
            # Vehicle Permissions
            'can_view_vehicles', 'can_add_vehicles', 'can_edit_vehicles', 'can_delete_vehicles',
            # Repair Permissions
            'can_view_repairs', 'can_add_repairs', 'can_edit_repairs', 'can_delete_repairs', 'can_complete_repairs',
            # PMS Permissions
            'can_view_pms', 'can_add_pms', 'can_edit_pms', 'can_delete_pms', 'can_complete_pms',
            # Inspection Permissions
            'can_view_inspections', 'can_add_inspections', 'can_edit_inspections', 'can_delete_inspections', 'can_approve_inspections',
            # User Management Permissions
            'can_view_users', 'can_add_users', 'can_edit_users', 'can_delete_users',
            # Department Management Permissions
            'can_view_departments', 'can_add_departments', 'can_edit_departments', 'can_delete_departments',
            # Driver Management Permissions
            'can_view_drivers', 'can_add_drivers', 'can_edit_drivers', 'can_delete_drivers',
            # Repair Shop Management Permissions
            'can_view_repair_shops', 'can_add_repair_shops', 'can_edit_repair_shops', 'can_delete_repair_shops',
            # System Permissions
            'can_view_reports', 'can_view_operational_status', 'can_view_activity_logs', 'can_view_admin_dashboard',
            'can_view_system_manual', 'can_view_notifications', 'can_mark_notifications_read'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords don't match.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class RepairShopForm(forms.ModelForm):
    class Meta:
        model = RepairShop
        fields = ['name', 'address', 'phone', 'email', 'contact_person', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PreInspectionReportForm(forms.ModelForm):
    class Meta:
        model = PreInspectionReport
        fields = [
            'vehicle', 'report_type', 'inspected_by',
            'engine_condition', 'transmission_condition', 'brakes_condition',
            'suspension_condition', 'electrical_condition', 'body_condition',
            'tires_condition', 'lights_condition', 'current_mileage', 'fuel_level',
            'issues_found', 'safety_concerns', 'recommended_actions'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'inspected_by': forms.Select(attrs={'class': 'form-control'}),
            'engine_condition': forms.Select(attrs={'class': 'form-control'}),
            'transmission_condition': forms.Select(attrs={'class': 'form-control'}),
            'brakes_condition': forms.Select(attrs={'class': 'form-control'}),
            'suspension_condition': forms.Select(attrs={'class': 'form-control'}),
            'electrical_condition': forms.Select(attrs={'class': 'form-control'}),
            'body_condition': forms.Select(attrs={'class': 'form-control'}),
            'tires_condition': forms.Select(attrs={'class': 'form-control'}),
            'lights_condition': forms.Select(attrs={'class': 'form-control'}),
            'current_mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuel_level': forms.Select(attrs={'class': 'form-control'}),
            'issues_found': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'safety_concerns': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommended_actions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values for condition fields
        for field_name in ['engine_condition', 'transmission_condition', 'brakes_condition',
                          'suspension_condition', 'electrical_condition', 'body_condition',
                          'tires_condition', 'lights_condition']:
            if not self.instance.pk:  # Only for new instances
                self.fields[field_name].initial = 'good'


class PostInspectionReportForm(forms.ModelForm):
    class Meta:
        model = PostInspectionReport
        fields = [
            'vehicle', 'report_type', 'inspected_by', 'pre_inspection',
            'work_completed_satisfactorily', 'quality_of_work', 'timeliness', 'cleanliness',
            'engine_condition', 'transmission_condition', 'brakes_condition',
            'suspension_condition', 'electrical_condition', 'body_condition',
            'tires_condition', 'lights_condition', 'test_drive_performed',
            'test_drive_distance', 'test_drive_notes', 'remaining_issues',
            'future_recommendations', 'warranty_notes'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'inspected_by': forms.Select(attrs={'class': 'form-control'}),
            'pre_inspection': forms.Select(attrs={'class': 'form-control'}),
            'work_completed_satisfactorily': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quality_of_work': forms.Select(attrs={'class': 'form-control'}),
            'timeliness': forms.Select(attrs={'class': 'form-control'}),
            'cleanliness': forms.Select(attrs={'class': 'form-control'}),
            'engine_condition': forms.Select(attrs={'class': 'form-control'}),
            'transmission_condition': forms.Select(attrs={'class': 'form-control'}),
            'brakes_condition': forms.Select(attrs={'class': 'form-control'}),
            'suspension_condition': forms.Select(attrs={'class': 'form-control'}),
            'electrical_condition': forms.Select(attrs={'class': 'form-control'}),
            'body_condition': forms.Select(attrs={'class': 'form-control'}),
            'tires_condition': forms.Select(attrs={'class': 'form-control'}),
            'lights_condition': forms.Select(attrs={'class': 'form-control'}),
            'test_drive_performed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'test_drive_distance': forms.NumberInput(attrs={'class': 'form-control'}),
            'test_drive_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'remaining_issues': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'future_recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'warranty_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values for condition fields
        for field_name in ['engine_condition', 'transmission_condition', 'brakes_condition',
                          'suspension_condition', 'electrical_condition', 'body_condition',
                          'tires_condition', 'lights_condition']:
            if not self.instance.pk:  # Only for new instances
                self.fields[field_name].initial = 'good'
        
        # Set default values for satisfaction fields
        for field_name in ['quality_of_work', 'timeliness', 'cleanliness']:
            if not self.instance.pk:  # Only for new instances
                self.fields[field_name].initial = 'good'
