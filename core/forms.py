from django import forms
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory
from .models import Vehicle, Repair, Driver, Division, RepairShop, RepairPart, RepairPartItem, PMS

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


# Create formset factory
RepairPartItemFormSet = inlineformset_factory(
    Repair, 
    RepairPartItem, 
    form=RepairPartItemForm,
    extra=0,  # No extra forms by default
    can_delete=True,
    can_delete_extra=False
)


class RepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = [
            'vehicle', 'date_of_repair', 'description',
            'cost', 'labor_cost', 'repair_shop', 'technician', 'status'
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
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active repair shops in the dropdown
        self.fields['repair_shop'].queryset = RepairShop.objects.filter(is_active=True)
        self.fields['repair_shop'].empty_label = "Select a repair shop..."


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
            'provider', 'technician', 'description', 'notes', 'status'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'service_type': forms.TextInput(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'completed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mileage_at_service': forms.NumberInput(attrs={'class': 'form-control'}),
            'next_service_mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'provider': forms.HiddenInput(),  # Will be populated by repair_shop
            'technician': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set the queryset for repair_shop field
        self.fields['repair_shop'].queryset = RepairShop.objects.filter(is_active=True)
        
        # Set default service type to 'General Inspection'
        if not self.instance.pk or not self.instance.service_type:
            self.fields['service_type'].initial = 'General Inspection'
        
        # If editing and there's a provider, try to find matching repair shop
        if self.instance.pk and self.instance.provider:
            try:
                repair_shop = RepairShop.objects.get(name=self.instance.provider)
                self.fields['repair_shop'].initial = repair_shop.id
            except (RepairShop.DoesNotExist, RepairShop.MultipleObjectsReturned):
                pass
    
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
