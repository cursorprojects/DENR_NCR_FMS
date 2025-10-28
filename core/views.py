from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
import json
from .models import Vehicle, Repair, Driver, Department, ActivityLog, RepairShop
from .forms import VehicleForm, RepairForm, DriverForm, DepartmentForm, UserForm, RepairShopForm, RepairPartItemFormSet

User = get_user_model()


@login_required
def dashboard(request):
    # Total vehicles
    total_vehicles = Vehicle.objects.count()
    
    # Status counts
    operational = Vehicle.objects.filter(status='Serviceable').count()
    under_repair = Vehicle.objects.filter(status='Under Repair').count()
    non_operational = Vehicle.objects.filter(status='Unserviceable').count()
    
    # Repair costs
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    monthly_cost = Repair.objects.filter(
        date_of_repair__month=current_month,
        date_of_repair__year=current_year,
        status='Completed'
    ).aggregate(total=Sum('cost'))['total'] or 0
    
    yearly_cost = Repair.objects.filter(
        date_of_repair__year=current_year,
        status='Completed'
    ).aggregate(total=Sum('cost'))['total'] or 0
    
    # Recent repairs
    recent_repairs = Repair.objects.all()[:5]
    
    # Monthly repair costs for the last 12 months
    monthly_costs = []
    for i in range(11, -1, -1):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        
        cost = Repair.objects.filter(
            date_of_repair__month=month,
            date_of_repair__year=year,
            status='Completed'
        ).aggregate(total=Sum('cost'))['total'] or 0
        
        monthly_costs.append({
            'month': datetime(year, month, 1).strftime('%b %Y'),
            'cost': float(cost)
        })
    
    context = {
        'total_vehicles': total_vehicles,
        'operational': operational,
        'under_repair': under_repair,
        'non_operational': non_operational,
        'monthly_cost': monthly_cost,
        'yearly_cost': yearly_cost,
        'recent_repairs': recent_repairs,
        'monthly_costs': json.dumps(monthly_costs),
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    
    # Filtering
    status_filter = request.GET.get('status', '')
    department_filter = request.GET.get('department', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)
    if department_filter:
        vehicles = vehicles.filter(department_id=department_filter)
    if search_query:
        vehicles = vehicles.filter(
            Q(plate_number__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(model__icontains=search_query)
        )
    
    departments = Department.objects.all()
    
    context = {
        'vehicles': vehicles,
        'departments': departments,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'search_query': search_query,
    }
    
    return render(request, 'core/vehicle_list.html', context)


@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    repairs = vehicle.repairs.all()
    total_repair_cost = repairs.filter(status='Completed').aggregate(total=Sum('cost'))['total'] or 0
    
    context = {
        'vehicle': vehicle,
        'repairs': repairs,
        'total_repair_cost': total_repair_cost,
    }
    
    return render(request, 'core/vehicle_detail.html', context)


@login_required
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle created successfully!')
            return redirect('vehicle_list')
    else:
        form = VehicleForm()
    
    return render(request, 'core/vehicle_form.html', {'form': form, 'title': 'Add Vehicle'})


@login_required
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle updated successfully!')
            return redirect('vehicle_detail', pk=pk)
    else:
        form = VehicleForm(instance=vehicle)
    
    return render(request, 'core/vehicle_form.html', {'form': form, 'title': 'Edit Vehicle'})


@login_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Vehicle deleted successfully!')
        return redirect('vehicle_list')
    return render(request, 'core/vehicle_delete.html', {'vehicle': vehicle})


@login_required
def repair_detail(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    return render(request, 'core/repair_detail.html', {'repair': repair})


@login_required
def repair_list(request):
    repairs = Repair.objects.all()
    
    # Filtering
    vehicle_filter = request.GET.get('vehicle', '')
    status_filter = request.GET.get('status', '')
    
    if vehicle_filter:
        repairs = repairs.filter(vehicle_id=vehicle_filter)
    if status_filter:
        repairs = repairs.filter(status=status_filter)
    
    vehicles = Vehicle.objects.all()
    
    context = {
        'repairs': repairs,
        'vehicles': vehicles,
        'vehicle_filter': vehicle_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'core/repair_list.html', context)


@login_required
def repair_create(request):
    if request.method == 'POST':
        form = RepairForm(request.POST)
        formset = RepairPartItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            repair = form.save()
            formset.instance = repair
            formset.save()
            # If vehicle is marked as damaged, update its status
            if 'damaged' in repair.description.lower() or repair.status == 'Ongoing':
                repair.vehicle.status = 'Damaged'
                repair.vehicle.save()
            messages.success(request, 'Repair record created successfully!')
            return redirect('repair_list')
    else:
        form = RepairForm()
        formset = RepairPartItemFormSet()
    
    return render(request, 'core/repair_form.html', {'form': form, 'formset': formset, 'title': 'Add Repair Record'})


@login_required
def repair_edit(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    if request.method == 'POST':
        form = RepairForm(request.POST, instance=repair)
        formset = RepairPartItemFormSet(request.POST, instance=repair)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Repair record updated successfully!')
            return redirect('repair_list')
    else:
        form = RepairForm(instance=repair)
        formset = RepairPartItemFormSet(instance=repair)
    
    return render(request, 'core/repair_form.html', {'form': form, 'formset': formset, 'title': 'Edit Repair Record'})


@login_required
def repair_delete(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    if request.method == 'POST':
        repair.delete()
        messages.success(request, 'Repair record deleted successfully!')
        return redirect('repair_list')
    return render(request, 'core/repair_delete.html', {'repair': repair})


@login_required
def operational_status(request):
    operational = Vehicle.objects.filter(status='Serviceable')
    under_repair = Vehicle.objects.filter(status='Under Repair')
    non_operational = Vehicle.objects.filter(status='Unserviceable')
    
    context = {
        'operational': operational,
        'under_repair': under_repair,
        'non_operational': non_operational,
    }
    
    return render(request, 'core/operational_status.html', context)


@login_required
def reports(request):
    # Monthly repair costs
    monthly_report = []
    for month in range(1, 13):
        cost = Repair.objects.filter(
            date_of_repair__month=month,
            date_of_repair__year=timezone.now().year,
            status='Completed'
        ).aggregate(total=Sum('cost'))['total'] or 0
        monthly_report.append({
            'month': datetime(2024, month, 1).strftime('%B'),
            'cost': cost
        })
    
    # Repair costs by vehicle
    vehicle_report = []
    for vehicle in Vehicle.objects.all():
        total = vehicle.total_repair_costs
        if total > 0:
            vehicle_report.append({
                'vehicle': vehicle.plate_number,
                'cost': total
            })
    
    # Repair costs by department
    department_report = []
    for dept in Department.objects.all():
        vehicles = dept.vehicle_set.all()
        total = sum(v.total_repair_costs for v in vehicles)
        if total > 0:
            department_report.append({
                'department': dept.name,
                'cost': total
            })
    
    context = {
        'monthly_report': monthly_report,
        'vehicle_report': vehicle_report,
        'department_report': department_report,
    }
    
    return render(request, 'core/reports.html', context)


# Authentication Views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.status == 'active':
                login(request, user)
                # Log activity
                ActivityLog.objects.create(
                    user=user,
                    action='login',
                    model_name='User',
                    description=f'User {user.get_full_name()} logged in',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Your account is inactive. Please contact an administrator.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')


def logout_view(request):
    if request.user.is_authenticated:
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='logout',
            model_name='User',
            description=f'User {request.user.get_full_name()} logged out',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


# User Management Views
@login_required
def user_list(request):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    users = User.objects.all()
    
    # Filtering
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    if role_filter:
        users = users.filter(role=role_filter)
    if status_filter:
        users = users.filter(status=status_filter)
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'core/cms/user_list.html', context)


@login_required
def user_create(request):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.created_by = request.user
            user.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='User',
                object_id=user.id,
                description=f'Created user {user.get_full_name()} with role {user.get_role_display()}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'User created successfully!')
            return redirect('user_list')
    else:
        form = UserForm()
    
    return render(request, 'core/cms/user_form.html', {'form': form, 'title': 'Add User'})


@login_required
def user_edit(request, pk):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='User',
                object_id=user.id,
                description=f'Updated user {user.get_full_name()}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'User updated successfully!')
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    
    return render(request, 'core/cms/user_form.html', {'form': form, 'title': 'Edit User'})


@login_required
def user_delete(request, pk):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='User',
            object_id=user.id,
            description=f'Deleted user {user.get_full_name()}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('user_list')
    
    return render(request, 'core/cms/user_delete.html', {'user_obj': user})


@login_required
def activity_logs(request):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    logs = ActivityLog.objects.all()[:100]  # Show last 100 activities
    
    context = {
        'logs': logs,
    }
    
    return render(request, 'core/cms/activity_logs.html', context)


@login_required
def admin_dashboard(request):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(status='active').count()
    inactive_users = User.objects.filter(status='inactive').count()
    
    # Role statistics
    super_admins = User.objects.filter(role='super_admin').count()
    fleet_managers = User.objects.filter(role='fleet_manager').count()
    encoders = User.objects.filter(role='encoder').count()
    
    # Recent activity
    recent_logs = ActivityLog.objects.all()[:10]
    
    # Vehicle statistics
    total_vehicles = Vehicle.objects.count()
    operational_vehicles = Vehicle.objects.filter(status='Serviceable').count()
    under_repair_vehicles = Vehicle.objects.filter(status='Under Repair').count()
    unserviceable_vehicles = Vehicle.objects.filter(status='Unserviceable').count()
    
    # Repair statistics
    total_repairs = Repair.objects.count()
    completed_repairs = Repair.objects.filter(status='Completed').count()
    ongoing_repairs = Repair.objects.filter(status='Ongoing').count()
    
    # Department, Driver, and Repair Shop statistics
    total_departments = Department.objects.count()
    total_drivers = Driver.objects.count()
    total_repair_shops = RepairShop.objects.count()
    active_repair_shops = RepairShop.objects.filter(is_active=True).count()
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'super_admins': super_admins,
        'fleet_managers': fleet_managers,
        'encoders': encoders,
        'recent_logs': recent_logs,
        'total_vehicles': total_vehicles,
        'operational_vehicles': operational_vehicles,
        'under_repair_vehicles': under_repair_vehicles,
        'unserviceable_vehicles': unserviceable_vehicles,
        'total_repairs': total_repairs,
        'completed_repairs': completed_repairs,
        'ongoing_repairs': ongoing_repairs,
        'total_departments': total_departments,
        'total_drivers': total_drivers,
        'total_repair_shops': total_repair_shops,
        'active_repair_shops': active_repair_shops,
    }
    
    return render(request, 'core/cms/admin_dashboard.html', context)


# Department Management Views
@login_required
def department_list(request):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    departments = Department.objects.all()
    
    # Filtering
    search_query = request.GET.get('search', '')
    if search_query:
        departments = departments.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'departments': departments,
        'search_query': search_query,
    }
    
    return render(request, 'core/cms/department_list.html', context)


@login_required
def department_create(request):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='Department',
                object_id=department.id,
                description=f'Created department {department.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Department created successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    
    return render(request, 'core/cms/department_form.html', {'form': form, 'title': 'Add Department'})


@login_required
def department_edit(request, pk):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='Department',
                object_id=department.id,
                description=f'Updated department {department.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Department updated successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'core/cms/department_form.html', {'form': form, 'title': 'Edit Department'})


@login_required
def department_delete(request, pk):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Department',
            object_id=department.id,
            description=f'Deleted department {department.name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        department.delete()
        messages.success(request, 'Department deleted successfully!')
        return redirect('department_list')
    
    return render(request, 'core/cms/department_delete.html', {'department': department})


# Driver Management Views
@login_required
def driver_list(request):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    drivers = Driver.objects.all()
    
    # Filtering
    search_query = request.GET.get('search', '')
    if search_query:
        drivers = drivers.filter(
            Q(name__icontains=search_query) |
            Q(license_number__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    context = {
        'drivers': drivers,
        'search_query': search_query,
    }
    
    return render(request, 'core/cms/driver_list.html', context)


@login_required
def driver_create(request):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            driver = form.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='Driver',
                object_id=driver.id,
                description=f'Created driver {driver.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Driver created successfully!')
            return redirect('driver_list')
    else:
        form = DriverForm()
    
    return render(request, 'core/cms/driver_form.html', {'form': form, 'title': 'Add Driver'})


@login_required
def driver_edit(request, pk):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    driver = get_object_or_404(Driver, pk=pk)
    
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='Driver',
                object_id=driver.id,
                description=f'Updated driver {driver.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Driver updated successfully!')
            return redirect('driver_list')
    else:
        form = DriverForm(instance=driver)
    
    return render(request, 'core/cms/driver_form.html', {'form': form, 'title': 'Edit Driver'})


@login_required
def driver_delete(request, pk):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    driver = get_object_or_404(Driver, pk=pk)
    
    if request.method == 'POST':
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Driver',
            object_id=driver.id,
            description=f'Deleted driver {driver.name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        driver.delete()
        messages.success(request, 'Driver deleted successfully!')
        return redirect('driver_list')
    
    return render(request, 'core/cms/driver_delete.html', {'driver': driver})


# Repair Shop Management Views
@login_required
def repairshop_list(request):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    repair_shops = RepairShop.objects.all()
    
    # Filtering
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        repair_shops = repair_shops.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if status_filter:
        repair_shops = repair_shops.filter(is_active=(status_filter == 'active'))
    
    context = {
        'repair_shops': repair_shops,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'core/cms/repairshop_list.html', context)


@login_required
def repairshop_create(request):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RepairShopForm(request.POST)
        if form.is_valid():
            repair_shop = form.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='RepairShop',
                object_id=repair_shop.id,
                description=f'Created repair shop {repair_shop.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Repair shop created successfully!')
            return redirect('repairshop_list')
    else:
        form = RepairShopForm()
    
    return render(request, 'core/cms/repairshop_form.html', {'form': form, 'title': 'Add Repair Shop'})


@login_required
def repairshop_edit(request, pk):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    repair_shop = get_object_or_404(RepairShop, pk=pk)
    
    if request.method == 'POST':
        form = RepairShopForm(request.POST, instance=repair_shop)
        if form.is_valid():
            form.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='RepairShop',
                object_id=repair_shop.id,
                description=f'Updated repair shop {repair_shop.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Repair shop updated successfully!')
            return redirect('repairshop_list')
    else:
        form = RepairShopForm(instance=repair_shop)
    
    return render(request, 'core/cms/repairshop_form.html', {'form': form, 'title': 'Edit Repair Shop'})


@login_required
def repairshop_delete(request, pk):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    repair_shop = get_object_or_404(RepairShop, pk=pk)
    
    if request.method == 'POST':
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='RepairShop',
            object_id=repair_shop.id,
            description=f'Deleted repair shop {repair_shop.name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        repair_shop.delete()
        messages.success(request, 'Repair shop deleted successfully!')
        return redirect('repairshop_list')
    
    return render(request, 'core/cms/repairshop_delete.html', {'repair_shop': repair_shop})
