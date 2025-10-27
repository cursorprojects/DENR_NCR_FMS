from django import forms
from django.contrib.auth import get_user_model
from .models import Vehicle, Repair, Driver, Department, RepairShop, RepairPart

User = get_user_model()


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'plate_number', 'vehicle_type', 'model', 'brand', 'year',
            'department', 'assigned_driver', 'status', 'date_acquired',
            'current_mileage', 'rfid_number', 'rfid_type', 'fleet_card_number',
            'gas_station', 'photo', 'registration_document', 'notes'
        ]
        widgets = {
            'plate_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
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


class RepairForm(forms.ModelForm):
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
    
    part_unit = forms.ChoiceField(choices=UNIT_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Repair
        fields = [
            'vehicle', 'date_of_repair', 'description', 'repairing_part',
            'part_additional_info', 'part_quantity', 'part_unit', 'disposal_type',
            'cost', 'repair_shop', 'technician', 'status'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'date_of_repair': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'repairing_part': forms.Select(attrs={'class': 'form-control'}),
            'part_additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'part_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'disposal_type': forms.Select(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'repair_shop': forms.Select(attrs={'class': 'form-control'}),
            'technician': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active repair shops in the dropdown
        self.fields['repair_shop'].queryset = RepairShop.objects.filter(is_active=True)
        self.fields['repair_shop'].empty_label = "Select a repair shop..."
        # Only show active repair parts in the dropdown
        self.fields['repairing_part'].queryset = RepairPart.objects.filter(is_active=True)
        self.fields['repairing_part'].empty_label = "Select a part..."
        self.fields['repairing_part'].label = "Part Replaced"
        
        # If editing, populate the unit field
        if self.instance and self.instance.pk:
            self.fields['part_unit'].initial = self.instance.part_unit


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


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


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
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'status', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
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
