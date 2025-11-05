from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django import forms
import json
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
import json
from .models import Vehicle, Repair, Driver, Division, ActivityLog, RepairShop, PMS, Notification, PreInspectionReport, PostInspectionReport
from .forms import VehicleForm, RepairForm, DriverForm, DivisionForm, UserForm, RepairShopForm, RepairPartItemFormSet, PMSForm, PMSRepairPartItemFormSet, PreInspectionReportForm, PostInspectionReportForm

User = get_user_model()


@login_required
def dashboard(request):
    try:
        # Total vehicles
        total_vehicles = Vehicle.objects.count()
        
        # Status counts
        operational = Vehicle.objects.filter(status='Serviceable').count()
        under_repair = Vehicle.objects.filter(status='Under Repair').count()
        non_operational = Vehicle.objects.filter(status='Unserviceable').count()
        
        # Vehicles breakdown by type for all statuses
        total_by_type = Vehicle.objects.values('vehicle_type').annotate(count=Count('id')).order_by('-count')
        total_type_breakdown = {item['vehicle_type']: item['count'] for item in total_by_type}
        
        serviceable_by_type = Vehicle.objects.filter(status='Serviceable').values('vehicle_type').annotate(count=Count('id')).order_by('-count')
        serviceable_type_breakdown = {item['vehicle_type']: item['count'] for item in serviceable_by_type}
        
        under_repair_by_type = Vehicle.objects.filter(status='Under Repair').values('vehicle_type').annotate(count=Count('id')).order_by('-count')
        under_repair_type_breakdown = {item['vehicle_type']: item['count'] for item in under_repair_by_type}
        
        non_operational_by_type = Vehicle.objects.filter(status='Unserviceable').values('vehicle_type').annotate(count=Count('id')).order_by('-count')
        non_operational_type_breakdown = {item['vehicle_type']: item['count'] for item in non_operational_by_type}
        
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
        
        # Vehicles near PMS (check for scheduled PMS within 1 month)
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        today = timezone.now().date()
        one_month_from_now = today + relativedelta(months=1)
        
        vehicles_near_pms = []
        all_vehicles = Vehicle.objects.filter(status='Serviceable')
        
        for vehicle in all_vehicles:
            # Check for overdue PMS first (highest priority)
            overdue_pms = PMS.objects.filter(
                vehicle=vehicle,
                status__in=['Scheduled', 'Overdue'],
                scheduled_date__lt=today
            ).order_by('scheduled_date').first()
            
            needs_pms = False
            reason = ""
            scheduled_date = None
            days_until = None
            pms_record = None
            
            if overdue_pms:
                # Found an overdue PMS - show this first (highest priority)
                needs_pms = True
                pms_record = overdue_pms
                scheduled_date = overdue_pms.scheduled_date
                days_overdue = (today - scheduled_date).days
                reason = f"PMS overdue by {days_overdue} day{'s' if days_overdue != 1 else ''} ({scheduled_date.strftime('%b %d, %Y')})"
            else:
                # Get upcoming scheduled PMS records that are within 1 month
                upcoming_pms = PMS.objects.filter(
                    vehicle=vehicle,
                    status__in=['Scheduled', 'Overdue'],
                    scheduled_date__gte=today,
                    scheduled_date__lte=one_month_from_now
                ).order_by('scheduled_date').first()
                
                if upcoming_pms:
                    # Found a scheduled PMS within 1 month
                    needs_pms = True
                    pms_record = upcoming_pms
                    scheduled_date = upcoming_pms.scheduled_date
                    days_until = (scheduled_date - today).days
                    if days_until == 0:
                        reason = "PMS scheduled today"
                    elif days_until == 1:
                        reason = "PMS scheduled tomorrow"
                    else:
                        reason = f"PMS scheduled in {days_until} days ({scheduled_date.strftime('%b %d, %Y')})"
            
            if needs_pms:
                vehicles_near_pms.append({
                    'vehicle': vehicle,
                    'reason': reason,
                    'scheduled_date': scheduled_date,
                    'days_until': days_until,
                    'days_overdue': (today - scheduled_date).days if scheduled_date and scheduled_date < today else None,
                    'pms_record': pms_record
                })
        
        # Sort by urgency (overdue first, then by scheduled date - earliest first)
        vehicles_near_pms.sort(key=lambda x: (
            1 if x['days_overdue'] is not None else 0,  # Overdue first
            x['scheduled_date'] if x['scheduled_date'] else timezone.now().date()  # Earliest scheduled date first
        ))
        
        # Take top 5
        vehicles_near_pms = vehicles_near_pms[:5]
        
        # Note: unread_notifications and unread_count are now provided by context processor
        
        context = {
            'total_vehicles': total_vehicles,
            'operational': operational,
            'under_repair': under_repair,
            'non_operational': non_operational,
            'total_type_breakdown': total_type_breakdown,
            'serviceable_type_breakdown': serviceable_type_breakdown,
            'under_repair_type_breakdown': under_repair_type_breakdown,
            'non_operational_type_breakdown': non_operational_type_breakdown,
            'monthly_cost': monthly_cost,
            'yearly_cost': yearly_cost,
            'recent_repairs': recent_repairs,
            'vehicles_near_pms': vehicles_near_pms,
        }
        
        return render(request, 'core/dashboard.html', context)
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        error_message = str(e)
        error_traceback = traceback.format_exc()
        logger.error(f"Dashboard error: {error_message}\n{error_traceback}")
        
        # Return error page with details if DEBUG is True
        from django.conf import settings
        if settings.DEBUG:
            from django.http import HttpResponse
            return HttpResponse(f"""
                <h1>Dashboard Error</h1>
                <h2>Error: {error_message}</h2>
                <pre style="background: #f5f5f5; padding: 20px; overflow: auto;">{error_traceback}</pre>
                <p><a href="/">Go back</a></p>
            """, content_type='text/html', status=500)
        else:
            messages.error(request, f'An error occurred: {error_message}')
            return redirect('login')


@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    
    # Filtering
    status_filter = request.GET.get('status', '')
    division_filter = request.GET.get('division', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)
    if division_filter:
        vehicles = vehicles.filter(division_id=division_filter)
    if search_query:
        vehicles = vehicles.filter(
            Q(plate_number__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(model__icontains=search_query)
        )
    
    # Check and mark vehicles for disposal based on repair costs
    for vehicle in vehicles:
        if vehicle.current_market_value:  # Only check if current market value is set
            vehicle.check_and_mark_for_disposal(user=request.user)
    
    divisions = Division.objects.all()
    
    # Prepare vehicle data with overuse information for template
    vehicle_data = []
    for vehicle in vehicles:
        is_overuse = False
        overuse_info = None
        disposal_percentage = None
        
        if vehicle.current_market_value:
            threshold = vehicle.disposal_threshold
            total_costs = vehicle.total_repair_costs
            if threshold and threshold > 0:
                # Calculate percentage of threshold used (can be > 100%)
                from decimal import Decimal
                percentage = float(total_costs / threshold * Decimal('100'))
                disposal_percentage = percentage
                
                if total_costs >= threshold:
                    is_overuse = True
                    overuse_info = {
                        'total_costs': total_costs,
                        'threshold': threshold,
                        'percentage': disposal_percentage,
                    }
                else:
                    # Still show info even if not at threshold yet
                    overuse_info = {
                        'total_costs': total_costs,
                        'threshold': threshold,
                        'percentage': disposal_percentage,
                    }
        
        vehicle_data.append({
            'vehicle': vehicle,
            'is_overuse': is_overuse,
            'overuse_info': overuse_info,
            'disposal_percentage': disposal_percentage,
        })
    
    context = {
        'vehicle_data': vehicle_data,
        'vehicles': vehicles,  # Keep for backward compatibility
        'divisions': divisions,
        'status_filter': status_filter,
        'division_filter': division_filter,
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
            vehicle = form.save(commit=False)
            
            # Handle multiple photos
            photos_list = []
            if 'photos' in request.FILES:
                photos_list = [f for f in request.FILES.getlist('photos')]
            # Also check for legacy 'photo' field
            if 'photo' in request.FILES:
                photos_list.extend([f for f in request.FILES.getlist('photo')])
            
            if photos_list:
                from django.core.files.storage import default_storage
                photo_paths = []
                for photo in photos_list:
                    if photo:
                        path = default_storage.save(f'vehicles/photos/{photo.name}', photo)
                        photo_paths.append(path)
                vehicle.photos = photo_paths
            
            # Handle multiple registration documents
            documents_list = []
            if 'registration_documents' in request.FILES:
                documents_list = [f for f in request.FILES.getlist('registration_documents')]
            # Also check for legacy 'registration_document' field
            if 'registration_document' in request.FILES:
                documents_list.extend([f for f in request.FILES.getlist('registration_document')])
            
            if documents_list:
                from django.core.files.storage import default_storage
                doc_paths = []
                for doc in documents_list:
                    if doc:
                        path = default_storage.save(f'documents/registration/{doc.name}', doc)
                        doc_paths.append(path)
                vehicle.registration_documents = doc_paths
            
            vehicle.save()
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
            vehicle = form.save(commit=False)
            
            # Get existing files
            existing_photos = vehicle.photos if vehicle.photos else []
            existing_documents = vehicle.registration_documents if vehicle.registration_documents else []
            
            # Handle multiple photos
            photos_list = []
            if 'photos' in request.FILES:
                photos_list = [f for f in request.FILES.getlist('photos')]
            # Also check for legacy 'photo' field
            if 'photo' in request.FILES:
                photos_list.extend([f for f in request.FILES.getlist('photo')])
            
            if photos_list:
                from django.core.files.storage import default_storage
                photo_paths = existing_photos.copy()
                for photo in photos_list:
                    if photo:
                        path = default_storage.save(f'vehicles/photos/{photo.name}', photo)
                        photo_paths.append(path)
                vehicle.photos = photo_paths
            
            # Handle multiple registration documents
            documents_list = []
            if 'registration_documents' in request.FILES:
                documents_list = [f for f in request.FILES.getlist('registration_documents')]
            # Also check for legacy 'registration_document' field
            if 'registration_document' in request.FILES:
                documents_list.extend([f for f in request.FILES.getlist('registration_document')])
            
            if documents_list:
                from django.core.files.storage import default_storage
                doc_paths = existing_documents.copy()
                for doc in documents_list:
                    if doc:
                        path = default_storage.save(f'documents/registration/{doc.name}', doc)
                        doc_paths.append(path)
                vehicle.registration_documents = doc_paths
            
            vehicle.save()
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
def vehicle_status_change(request, pk):
    """Dedicated view for changing vehicle status"""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        reason = request.POST.get('reason', '')
        
        if new_status in [choice[0] for choice in Vehicle.STATUS_CHOICES]:
            old_status = vehicle.status
            vehicle.update_status(new_status, user=request.user, reason=reason)
            
            messages.success(
                request, 
                f'Vehicle status changed from {old_status} to {new_status} successfully!'
            )
            return redirect('vehicle_detail', pk=pk)
        else:
            messages.error(request, 'Invalid status selected.')
    
    context = {
        'vehicle': vehicle,
        'status_choices': Vehicle.STATUS_CHOICES,
    }
    
    return render(request, 'core/vehicle_status_change.html', context)


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
        
        try:
            if form.is_valid() and formset.is_valid():
                repair = form.save()
                formset.instance = repair
                formset.save()
                
                # Calculate and update the total parts cost
                total_parts_cost = sum(item.cost for item in repair.part_items.all() if item.cost)
                repair.cost = total_parts_cost
                repair.save()
                
                # If vehicle is marked as damaged, update its status
                if 'damaged' in repair.description.lower() or repair.status == 'Ongoing':
                    repair.vehicle.status = 'Damaged'
                    repair.vehicle.save()
                
                messages.success(request, 'Repair record created successfully!')
                return redirect('repair_list')
        except ValidationError as e:
            messages.error(request, str(e))
            # Re-render the form with errors
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = RepairForm()
        # For create mode, start with 1 empty form
        formset = RepairPartItemFormSet()
        formset.extra = 1
    
    return render(request, 'core/repair_form.html', {'form': form, 'formset': formset, 'title': 'Add Repair Record'})


@login_required
def repair_edit(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    if request.method == 'POST':
        form = RepairForm(request.POST, instance=repair)
        formset = RepairPartItemFormSet(request.POST, instance=repair)
        if form.is_valid() and formset.is_valid():
            repair = form.save()
            formset.save()
            
            # Calculate and update the total parts cost
            total_parts_cost = sum(item.cost for item in repair.part_items.all() if item.cost)
            repair.cost = total_parts_cost
            repair.save()
            
            messages.success(request, 'Repair record updated successfully!')
            return redirect('repair_list')
    else:
        form = RepairForm(instance=repair)
        formset = RepairPartItemFormSet(instance=repair)
        # For edit mode, only add extra form if no existing parts
        if repair.part_items.count() == 0:
            formset.extra = 1
        else:
            formset.extra = 0
    
    return render(request, 'core/repair_form.html', {'form': form, 'formset': formset, 'title': 'Edit Repair Record'})


@login_required
def repair_delete(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    if request.method == 'POST':
        vehicle = repair.vehicle
        repair.delete()
        # Recheck disposal status after repair deletion
        if vehicle.acquisition_cost:
            vehicle.refresh_from_db()
            vehicle.check_and_mark_for_disposal(user=request.user)
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
    
    # Repair costs by division
    division_report = []
    for dept in Division.objects.all():
        vehicles = dept.vehicle_set.all()
        total = sum(v.total_repair_costs for v in vehicles)
        if total > 0:
            division_report.append({
                'division': dept.name,
                'cost': total
            })
    
    context = {
        'monthly_report': monthly_report,
        'vehicle_report': vehicle_report,
        'division_report': division_report,
    }
    
    return render(request, 'core/reports.html', context)


@login_required
def notifications(request):
    """View all notifications for the current user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Don't automatically mark as read - user must manually click
    # This allows users to keep notifications visible until they explicitly mark them as read
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'core/notifications.html', context)


@csrf_exempt
@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})


@csrf_exempt
@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    
    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    return JsonResponse({'success': True})


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
    if not request.user.can_view_users:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    users = User.objects.all()
    
    # Filtering
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
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
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'core/cms/user_list.html', context)


@login_required
def user_create(request):
    if not request.user.can_add_users:
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
                description=f'Created user {user.get_full_name()}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'User created successfully!')
            return redirect('user_list')
    else:
        form = UserForm()
    
    return render(request, 'core/cms/user_form.html', {'form': form, 'title': 'Add User'})


@login_required
def user_edit(request, pk):
    if not request.user.can_edit_users:
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
    if not request.user.can_delete_users:
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
    if not request.user.can_view_admin_dashboard:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(status='active').count()
    inactive_users = User.objects.filter(status='inactive').count()
    
    # Permission statistics
    admin_users = User.objects.filter(can_view_admin_dashboard=True).count()
    manager_users = User.objects.filter(can_view_vehicles=True).count()
    staff_users = User.objects.filter(can_view_repairs=True).count()
    
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
    
    # Division, Driver, and Repair Shop statistics
    total_divisions = Division.objects.count()
    total_drivers = Driver.objects.count()
    total_repair_shops = RepairShop.objects.count()
    active_repair_shops = RepairShop.objects.filter(is_active=True).count()
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'admin_users': admin_users,
        'manager_users': manager_users,
        'staff_users': staff_users,
        'recent_logs': recent_logs,
        'total_vehicles': total_vehicles,
        'operational_vehicles': operational_vehicles,
        'under_repair_vehicles': under_repair_vehicles,
        'unserviceable_vehicles': unserviceable_vehicles,
        'total_repairs': total_repairs,
        'completed_repairs': completed_repairs,
        'ongoing_repairs': ongoing_repairs,
        'total_divisions': total_divisions,
        'total_drivers': total_drivers,
        'total_repair_shops': total_repair_shops,
        'active_repair_shops': active_repair_shops,
    }
    
    return render(request, 'core/cms/admin_dashboard.html', context)


# Division Management Views
@login_required
def division_list(request):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    divisions = Division.objects.all()
    
    # Filtering
    search_query = request.GET.get('search', '')
    if search_query:
        divisions = divisions.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'divisions': divisions,
        'search_query': search_query,
    }
    
    return render(request, 'core/cms/division_list.html', context)


@login_required
def division_create(request):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DivisionForm(request.POST)
        if form.is_valid():
            division = form.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='Division',
                object_id=division.id,
                description=f'Created division {division.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Division created successfully!')
            return redirect('division_list')
    else:
        form = DivisionForm()
    
    return render(request, 'core/cms/division_form.html', {'form': form, 'title': 'Add Division'})


@login_required
def division_edit(request, pk):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    division = get_object_or_404(Division, pk=pk)
    
    if request.method == 'POST':
        form = DivisionForm(request.POST, instance=division)
        if form.is_valid():
            form.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='Division',
                object_id=division.id,
                description=f'Updated division {division.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Division updated successfully!')
            return redirect('division_list')
    else:
        form = DivisionForm(instance=division)
    
    return render(request, 'core/cms/division_form.html', {'form': form, 'title': 'Edit Division'})


@login_required
def division_delete(request, pk):
    if not request.user.has_admin_access():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    division = get_object_or_404(Division, pk=pk)
    
    if request.method == 'POST':
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Division',
            object_id=division.id,
            description=f'Deleted division {division.name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        division.delete()
        messages.success(request, 'Division deleted successfully!')
        return redirect('division_list')
    
    return render(request, 'core/cms/division_delete.html', {'division': division})


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


# PMS Views
@login_required
def pms_list(request):
    """List all PMS records"""
    pms_records = PMS.objects.all().order_by('-scheduled_date')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        pms_records = pms_records.filter(status=status_filter)
    
    # Filter by vehicle
    vehicle_filter = request.GET.get('vehicle')
    if vehicle_filter:
        pms_records = pms_records.filter(vehicle_id=vehicle_filter)
    
    context = {
        'pms_records': pms_records,
        'vehicles': Vehicle.objects.all(),
        'status_choices': PMS.STATUS_CHOICES,
        'status_filter': status_filter,
        'vehicle_filter': vehicle_filter,
    }
    return render(request, 'core/pms_list.html', context)


@login_required
def pms_create(request):
    """Create new PMS record"""
    if request.method == 'POST':
        form = PMSForm(request.POST)
        
        # Check if there are any parts in the formset data
        # Find the formset prefix from POST data
        formset_prefix = None
        total_forms = 0
        has_parts_data = False
        
        # Find the TOTAL_FORMS field to determine prefix
        for key in request.POST.keys():
            if key.endswith('-TOTAL_FORMS'):
                formset_prefix = key.replace('-TOTAL_FORMS', '')
                total_forms = int(request.POST.get(key, 0))
                break
        
        # If we found a prefix, check if any form has a part selected
        if formset_prefix and total_forms > 0:
            for i in range(total_forms):
                part_value = request.POST.get(f'{formset_prefix}-{i}-part', '')
                delete_value = request.POST.get(f'{formset_prefix}-{i}-DELETE', '')
                if part_value and not delete_value:
                    has_parts_data = True
                    break
        
        # Validate form first
        form_valid = form.is_valid()
        
        # DEBUG: Check if form has errors after validation
        if form.errors:
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Form validation errors: {form.errors}")
            logger.debug(f"Form non_field_errors: {form.non_field_errors()}")
        
        # Create formset without instance for validation (like repair_create)
        formset = PMSRepairPartItemFormSet(request.POST)
        
        # Only validate formset if there are parts or if formset has data
        formset_valid = True
        if has_parts_data or total_forms > 0:
            formset_valid = formset.is_valid()
        
        try:
            if form_valid and formset_valid:
                # CRITICAL: If form has ANY errors, don't save - even if form_valid is True
                # This can happen if ValidationError was raised but form_valid wasn't properly set
                if form.errors:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"CRITICAL: Form has errors but form_valid is True! Errors: {form.errors}")
                    # Don't save - fall through to error handling
                    form_valid = False
                
                # Only save if form is truly valid (no errors)
                if form_valid and formset_valid and not form.errors:
                    # Save with skip_usage_validation=True since form already validated pre-inspection usage
                    pms = form.save(commit=False)
                    pms.save(skip_usage_validation=True)
                    
                    # Only proceed if we successfully saved (pms has a pk)
                    if not hasattr(pms, 'pk') or pms.pk is None:
                        # Save failed somehow, don't continue
                        messages.error(request, 'Failed to save PMS record. Please try again.')
                    else:
                        # Check if user selected any parts to replace
                        has_parts = False
                        parts_cost = 0
                        
                        for part_form in formset:
                            if part_form.cleaned_data and not part_form.cleaned_data.get('DELETE', False):
                                has_parts = True
                                cost = part_form.cleaned_data.get('cost') or 0
                                try:
                                    parts_cost += float(cost)
                                except (ValueError, TypeError):
                                    # Skip invalid cost values
                                    pass
                        
                        # If parts were replaced, create a repair record
                        if has_parts:
                            from django.utils import timezone
                            
                            # Get PMS service cost to use as labor cost
                            try:
                                pms_service_cost = float(pms.cost) if pms.cost else 0
                            except (ValueError, TypeError):
                                pms_service_cost = 0
                            
                            # Ensure parts_cost doesn't exceed max_digits (10 digits total, 8 before decimal, 2 after)
                            # max_digits=10, decimal_places=2 means max value is 99999999.99
                            max_cost = 99999999.99
                            if parts_cost > max_cost:
                                messages.warning(request, f'Total parts cost ({parts_cost:.2f}) exceeds maximum allowed ({max_cost:.2f}). It will be capped at maximum.')
                                parts_cost = max_cost
                            
                            # Create repair record for PMS with 'Ongoing' status initially
                            # It will be marked as 'Completed' when post-inspection is done
                            repair_data = {
                                'vehicle': pms.vehicle,
                                'date_of_repair': pms.scheduled_date,
                                'description': f"PMS: {pms.service_type}",
                                'cost': min(parts_cost, max_cost),  # Cap at maximum
                                'labor_cost': min(pms_service_cost, max_cost) if pms_service_cost else 0,
                                'repair_shop': form.cleaned_data.get('repair_shop'),
                                'technician': pms.technician,
                                'status': 'Ongoing',  # Start as Ongoing, not Completed
                            }
                            # Only add pre_inspection if it exists and is not None
                            if pms.pre_inspection_id:
                                try:
                                    # Verify the pre_inspection still exists by accessing the ID
                                    pre_inspection = PreInspectionReport.objects.get(pk=pms.pre_inspection_id)
                                    repair_data['pre_inspection'] = pre_inspection
                                except (PreInspectionReport.DoesNotExist, AttributeError):
                                    # Pre-inspection was deleted or doesn't exist, skip it
                                    pass
                            
                            # Create repair with skip_pms_validation=True since it's being created from PMS
                            # The repair can share the same pre_inspection as the PMS
                            # We need to create it without validation first, then save with skip_pms_validation
                            repair = Repair(**repair_data)
                            repair.save(skip_pms_validation=True)
                            
                            # Link repair to PMS
                            # Use update() to avoid triggering model validation again
                            # The form validation already checked everything
                            PMS.objects.filter(pk=pms.pk).update(repair=repair)
                            # Refresh the instance to get the updated repair
                            pms.refresh_from_db()
                            
                            # Create a new formset with the repair instance to ensure proper saving
                            # This is necessary because the formset was validated without an instance
                            repair_formset = PMSRepairPartItemFormSet(request.POST, instance=repair)
                            if repair_formset.is_valid():
                                repair_formset.save()
                            else:
                                # If validation fails, log error but don't fail the entire operation
                                import traceback
                                traceback.print_exc()
                                messages.warning(request, 'PMS created but some parts may not have been saved. Please check the repair record.')
                            
                            # Log activity
                            ActivityLog.objects.create(
                                user=request.user,
                                action='create',
                                model_name='Repair',
                                object_id=repair.id,
                                description=f'Created repair record for PMS: {pms.vehicle.plate_number}',
                                ip_address=request.META.get('REMOTE_ADDR')
                            )
                        
                        # Log activity for PMS
                        ActivityLog.objects.create(
                            user=request.user,
                            action='create',
                            model_name='PMS',
                            object_id=pms.id,
                            description=f'Created PMS record for {pms.vehicle.plate_number} - {pms.service_type}',
                            ip_address=request.META.get('REMOTE_ADDR')
                        )
                        
                        # Clear any form errors before redirecting (they shouldn't exist if we got here)
                        # But just to be safe, clear them explicitly
                        if hasattr(form, '_errors'):
                            form._errors = {}
                        
                        messages.success(request, 'PMS record created successfully!')
                        return redirect('pms_list')
                else:
                    # Form or formset was invalid, or save didn't happen
                    # Don't do anything here - let it fall through to error handling below
                    pass
            else:
                # Form or formset validation failed - errors will be displayed in template
                if form.errors:
                    # Check for non-field errors (ValidationError from clean() method)
                    if form.non_field_errors():
                        for error in form.non_field_errors():
                            messages.error(request, str(error))
                    # Check for field-specific errors
                    for field, errors in form.errors.items():
                        if field != '__all__':
                            for error in errors:
                                messages.error(request, f'{field}: {error}')
                if has_parts_data and formset.errors:
                    for i, form_errors in enumerate(formset.errors):
                        if form_errors:
                            for field, errors in form_errors.items():
                                for error in errors:
                                    messages.error(request, f'Part form {i+1} - {field}: {error}')
                    # Also check for non-form errors
                    # non_form_errors is a property that returns an ErrorList
                    try:
                        # Access non_form_errors as a property (not a method)
                        non_form_errors = getattr(formset, 'non_form_errors', None)
                        if non_form_errors:
                            # Convert to list if it's an ErrorList or other iterable
                            if hasattr(non_form_errors, '__iter__') and not isinstance(non_form_errors, (str, bytes)):
                                for error in non_form_errors:
                                    messages.error(request, f'Formset error: {error}')
                            elif isinstance(non_form_errors, str):
                                messages.error(request, f'Formset error: {non_form_errors}')
                    except Exception as e:
                        # If there's an issue accessing non_form_errors, skip it silently
                        pass
                # Re-create formset for display with errors
                if not form_valid:
                    formset = PMSRepairPartItemFormSet(request.POST) if has_parts_data else PMSRepairPartItemFormSet()
                elif has_parts_data:
                    # Form is valid but formset failed, recreate formset with form data
                    temp_repair = Repair()
                    temp_repair.vehicle = form.cleaned_data.get('vehicle')
                    formset = PMSRepairPartItemFormSet(request.POST, instance=temp_repair)
        except (ValidationError, forms.ValidationError) as e:
            messages.error(request, str(e))
            # Re-render the form with errors - ensure formset is created
            try:
                formset
            except NameError:
                formset = PMSRepairPartItemFormSet(request.POST) if has_parts_data else PMSRepairPartItemFormSet()
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            import traceback
            traceback.print_exc()
            # Ensure formset is created even on exception
            try:
                formset
            except NameError:
                formset = PMSRepairPartItemFormSet(request.POST) if has_parts_data else PMSRepairPartItemFormSet()
    else:
        form = PMSForm()
        formset = PMSRepairPartItemFormSet()
        # Pre-select vehicle if coming from vehicle detail
        vehicle_id = request.GET.get('vehicle')
        if vehicle_id:
            try:
                vehicle = Vehicle.objects.get(id=vehicle_id)
                form.fields['vehicle'].initial = vehicle
            except Vehicle.DoesNotExist:
                pass
    
    return render(request, 'core/pms_form.html', {'form': form, 'formset': formset, 'title': 'Add PMS Record'})


@login_required
def pms_edit(request, pk):
    """Edit PMS record"""
    pms = get_object_or_404(PMS, pk=pk)
    
    # Get the associated repair if it exists
    repair = pms.repair
    
    if request.method == 'POST':
        form = PMSForm(request.POST, instance=pms)
        formset = PMSRepairPartItemFormSet(request.POST, instance=repair) if repair else PMSRepairPartItemFormSet(request.POST)
        
        try:
            form_valid = form.is_valid()
            formset_valid = formset.is_valid()
            
            if form_valid and formset_valid:
                # Save with skip_usage_validation=True since form already validated pre-inspection usage
                pms = form.save(commit=False)
                
                # When editing, if pre_inspection is not provided, use the existing one
                if pms.pk and not pms.pre_inspection:
                    # Get the existing pre_inspection from the database
                    existing_pms = PMS.objects.get(pk=pms.pk)
                    pms.pre_inspection = existing_pms.pre_inspection
                
                pms.save(skip_usage_validation=True)
                
                # Refresh repair reference after saving (in case it was updated)
                repair = pms.repair
                
                # Check if user selected any parts to replace
                has_parts = False
                parts_cost = 0
                
                for part_form in formset:
                    if part_form.cleaned_data and not part_form.cleaned_data.get('DELETE', False):
                        has_parts = True
                        cost = part_form.cleaned_data.get('cost') or 0
                        try:
                            parts_cost += float(cost)
                        except (ValueError, TypeError):
                            # Skip invalid cost values
                            pass
                
                # If parts were selected and no repair exists, create one
                if has_parts and not repair:
                    # Get PMS service cost to use as labor cost
                    pms_service_cost = float(pms.cost) if pms.cost else 0
                    
                    # Create repair with 'Ongoing' status initially
                    # It will be marked as 'Completed' when post-inspection is done
                    repair_data = {
                        'vehicle': pms.vehicle,
                        'date_of_repair': pms.scheduled_date,
                        'description': f"PMS: {pms.service_type}",
                        'cost': parts_cost,
                        'labor_cost': pms_service_cost,
                        'repair_shop': form.cleaned_data.get('repair_shop'),
                        'technician': pms.technician,
                        'status': 'Ongoing',  # Start as Ongoing, not Completed
                    }
                    # Only add pre_inspection if it exists and is not None
                    if pms.pre_inspection_id:
                        try:
                            # Verify the pre_inspection still exists by accessing the ID
                            pre_inspection = PreInspectionReport.objects.get(pk=pms.pre_inspection_id)
                            repair_data['pre_inspection'] = pre_inspection
                        except (PreInspectionReport.DoesNotExist, AttributeError):
                            # Pre-inspection was deleted or doesn't exist, skip it
                            pass
                    
                    repair = Repair.objects.create(**repair_data)
                    # Use update() to avoid triggering model validation again
                    # The form validation already checked everything
                    PMS.objects.filter(pk=pms.pk).update(repair=repair)
                    # Refresh the instance to get the updated repair
                    pms.refresh_from_db()
                    
                    # Create a new formset with the repair instance to ensure proper saving
                    repair_formset = PMSRepairPartItemFormSet(request.POST, instance=repair)
                    if repair_formset.is_valid():
                        repair_formset.save()
                    else:
                        # If validation fails, log error but don't fail the entire operation
                        import traceback
                        traceback.print_exc()
                        messages.warning(request, 'PMS updated but some parts may not have been saved. Please check the repair record.')
                    
                    # Log activity for repair
                    ActivityLog.objects.create(
                        user=request.user,
                        action='create',
                        model_name='Repair',
                        object_id=repair.id,
                        description=f'Created repair record for PMS: {pms.vehicle.plate_number}',
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                elif repair:
                    # Update existing repair - set parts cost and labor cost
                    try:
                        pms_service_cost = float(pms.cost) if pms.cost else 0
                    except (ValueError, TypeError):
                        pms_service_cost = 0
                    
                    # Ensure costs don't exceed max_digits (10 digits total, 8 before decimal, 2 after)
                    max_cost = 99999999.99
                    if parts_cost > max_cost:
                        messages.warning(request, f'Total parts cost ({parts_cost:.2f}) exceeds maximum allowed ({max_cost:.2f}). It will be capped at maximum.')
                        parts_cost = max_cost
                    if pms_service_cost > max_cost:
                        messages.warning(request, f'Service cost ({pms_service_cost:.2f}) exceeds maximum allowed ({max_cost:.2f}). It will be capped at maximum.')
                        pms_service_cost = max_cost
                    
                    repair.cost = min(parts_cost, max_cost)
                    repair.labor_cost = min(pms_service_cost, max_cost) if pms_service_cost else 0
                    repair.save()
                    
                    # Create a new formset with the repair instance to ensure proper saving
                    repair_formset = PMSRepairPartItemFormSet(request.POST, instance=repair)
                    if repair_formset.is_valid():
                        repair_formset.save()
                    else:
                        # If validation fails, log error but don't fail the entire operation
                        import traceback
                        traceback.print_exc()
                        messages.warning(request, 'PMS updated but some parts may not have been saved. Please check the repair record.')
                
                # Log activity for PMS
                ActivityLog.objects.create(
                    user=request.user,
                    action='update',
                    model_name='PMS',
                    object_id=pms.id,
                    description=f'Updated PMS record for {pms.vehicle.plate_number} - {pms.service_type}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                
                messages.success(request, 'PMS record updated successfully!')
                return redirect('pms_list')
            else:
                # Form or formset validation failed - errors will be displayed in template
                if form.errors:
                    # Check for non-field errors (ValidationError from clean() method)
                    if form.non_field_errors():
                        for error in form.non_field_errors():
                            messages.error(request, str(error))
                    # Check for field-specific errors
                    for field, errors in form.errors.items():
                        if field != '__all__':
                            for error in errors:
                                messages.error(request, f'{field}: {error}')
                if formset.errors:
                    for i, form_errors in enumerate(formset.errors):
                        if form_errors:
                            for field, errors in form_errors.items():
                                for error in errors:
                                    messages.error(request, f'Part form {i+1} - {field}: {error}')
                    # Also check for non-form errors
                    # non_form_errors is a property that returns an ErrorList
                    try:
                        # Access non_form_errors as a property (not a method)
                        non_form_errors = getattr(formset, 'non_form_errors', None)
                        if non_form_errors:
                            # Convert to list if it's an ErrorList or other iterable
                            if hasattr(non_form_errors, '__iter__') and not isinstance(non_form_errors, (str, bytes)):
                                for error in non_form_errors:
                                    messages.error(request, f'Formset error: {error}')
                            elif isinstance(non_form_errors, str):
                                messages.error(request, f'Formset error: {non_form_errors}')
                    except Exception as e:
                        # If there's an issue accessing non_form_errors, skip it silently
                        pass
        except (ValidationError, forms.ValidationError) as e:
            messages.error(request, str(e))
            # Re-render the form with errors - ensure formset is created
            try:
                formset
            except NameError:
                formset = PMSRepairPartItemFormSet(request.POST, instance=repair) if repair else PMSRepairPartItemFormSet(request.POST)
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            import traceback
            traceback.print_exc()
            # Ensure formset is created even on exception
            try:
                formset
            except NameError:
                formset = PMSRepairPartItemFormSet(request.POST, instance=repair) if repair else PMSRepairPartItemFormSet(request.POST)
    else:
        form = PMSForm(instance=pms)
        if repair:
            formset = PMSRepairPartItemFormSet(instance=repair)
            if repair.part_items.count() == 0:
                formset.extra = 1
            else:
                formset.extra = 0
        else:
            formset = PMSRepairPartItemFormSet()
    
    return render(request, 'core/pms_form.html', {'form': form, 'formset': formset, 'title': 'Edit PMS Record', 'pms': pms, 'repair': repair})


@login_required
def pms_detail(request, pk):
    """View PMS record details"""
    pms = get_object_or_404(PMS, pk=pk)
    return render(request, 'core/pms_detail.html', {'pms': pms})


@login_required
def pms_delete(request, pk):
    """Delete PMS record"""
    pms = get_object_or_404(PMS, pk=pk)
    
    if request.method == 'POST':
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='PMS',
            object_id=pms.id,
            description=f'Deleted PMS record for {pms.vehicle.plate_number} - {pms.service_type}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        pms.delete()
        messages.success(request, 'PMS record deleted successfully!')
        return redirect('pms_list')
    
    return render(request, 'core/pms_delete.html', {'pms': pms})


# Inspection Report Views

@login_required
def pre_inspection_list(request):
    """List all pre-inspection reports"""
    reports = PreInspectionReport.objects.all().order_by('-inspection_date')
    
    # Get filter parameters
    availability_filter = request.GET.get('availability', '')
    vehicle_filter = request.GET.get('vehicle', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Apply filters
    if availability_filter == 'used':
        # Get IDs of reports used by repairs or PMS
        used_repair_ids = Repair.objects.exclude(pre_inspection__isnull=True).values_list('pre_inspection_id', flat=True)
        used_pms_ids = PMS.objects.exclude(pre_inspection__isnull=True).values_list('pre_inspection_id', flat=True)
        used_ids = set(list(used_repair_ids) + list(used_pms_ids))
        reports = reports.filter(id__in=used_ids)
    elif availability_filter == 'available':
        # Get IDs of reports used by repairs or PMS
        used_repair_ids = Repair.objects.exclude(pre_inspection__isnull=True).values_list('pre_inspection_id', flat=True)
        used_pms_ids = PMS.objects.exclude(pre_inspection__isnull=True).values_list('pre_inspection_id', flat=True)
        used_ids = set(list(used_repair_ids) + list(used_pms_ids))
        reports = reports.exclude(id__in=used_ids)
    
    if vehicle_filter:
        reports = reports.filter(vehicle_id=vehicle_filter)
    
    if date_from:
        try:
            from django.utils.dateparse import parse_datetime
            date_from_obj = parse_datetime(date_from) if 'T' in date_from else datetime.strptime(date_from, '%Y-%m-%d')
            if date_from_obj:
                reports = reports.filter(inspection_date__gte=date_from_obj)
        except (ValueError, TypeError):
            pass
    
    if date_to:
        try:
            from django.utils.dateparse import parse_datetime
            date_to_obj = parse_datetime(date_to) if 'T' in date_to else datetime.strptime(date_to, '%Y-%m-%d')
            if date_to_obj:
                # Add one day to include the full day
                from datetime import timedelta
                date_to_obj = date_to_obj + timedelta(days=1)
                reports = reports.filter(inspection_date__lt=date_to_obj)
        except (ValueError, TypeError):
            pass
    
    # Annotate each report with usage information
    for report in reports:
        # Check if used by a repair
        repair_usage = Repair.objects.filter(pre_inspection=report).first()
        # Check if used by a PMS
        pms_usage = PMS.objects.filter(pre_inspection=report).first()
        
        report.used_by_repair = repair_usage
        report.used_by_pms = pms_usage
        report.is_used = repair_usage is not None or pms_usage is not None
    
    # Get all vehicles for filter dropdown
    vehicles = Vehicle.objects.all().order_by('plate_number')
    
    context = {
        'reports': reports,
        'vehicles': vehicles,
        'availability_filter': availability_filter,
        'vehicle_filter': vehicle_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'core/pre_inspection_list.html', context)


@login_required
def pre_inspection_create(request):
    """Create a new pre-inspection report"""
    if request.method == 'POST':
        form = PreInspectionReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            # Always set inspected_by to current user (or use form value if provided)
            if not report.inspected_by:
                report.inspected_by = request.user
            
            # Handle multiple driver report attachments
            attachments_list = []
            if 'driver_report_attachments' in request.FILES:
                attachments_list = [f for f in request.FILES.getlist('driver_report_attachments')]
            # Also check for legacy 'driver_report_attachment' field
            if 'driver_report_attachment' in request.FILES:
                attachments_list.extend([f for f in request.FILES.getlist('driver_report_attachment')])
            
            if attachments_list:
                from django.core.files.storage import default_storage
                attachment_paths = []
                for attachment in attachments_list:
                    if attachment:
                        path = default_storage.save(f'pre_inspection/driver_reports/{attachment.name}', attachment)
                        attachment_paths.append(path)
                report.driver_report_attachments = attachment_paths
            
            report.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='PreInspectionReport',
                object_id=report.id,
                description=f'Created pre-inspection report for {report.vehicle.plate_number} - {report.get_report_type_display()}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Pre-inspection report created successfully!')
            return redirect('pre_inspection_detail', pk=report.pk)
    else:
        form = PreInspectionReportForm()
        # Set default inspected_by to current user
        form.fields['inspected_by'].initial = request.user
    
    return render(request, 'core/pre_inspection_form.html', {'form': form, 'title': 'Create Pre-Inspection Report'})


@login_required
def pre_inspection_detail(request, pk):
    """View pre-inspection report details"""
    report = get_object_or_404(PreInspectionReport, pk=pk)
    return render(request, 'core/pre_inspection_detail.html', {'report': report})


@login_required
def pre_inspection_edit(request, pk):
    """Edit pre-inspection report"""
    report = get_object_or_404(PreInspectionReport, pk=pk)
    
    if request.method == 'POST':
        form = PreInspectionReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            report = form.save(commit=False)
            
            # Ensure inspected_by is always set
            # If editing, preserve existing inspected_by if it exists, otherwise use form value or current user
            if report.pk:
                # Get existing inspected_by from database
                existing_report = PreInspectionReport.objects.get(pk=report.pk)
                # Use existing value if form didn't provide one, otherwise use form value
                if not report.inspected_by:
                    report.inspected_by = existing_report.inspected_by or request.user
            else:
                # New record - use form value or current user
                if not report.inspected_by:
                    report.inspected_by = request.user
            
            # Get existing attachments
            existing_attachments = report.driver_report_attachments if report.driver_report_attachments else []
            
            # Handle multiple driver report attachments
            attachments_list = []
            if 'driver_report_attachments' in request.FILES:
                attachments_list = [f for f in request.FILES.getlist('driver_report_attachments')]
            # Also check for legacy 'driver_report_attachment' field
            if 'driver_report_attachment' in request.FILES:
                attachments_list.extend([f for f in request.FILES.getlist('driver_report_attachment')])
            
            if attachments_list:
                from django.core.files.storage import default_storage
                attachment_paths = existing_attachments.copy()
                for attachment in attachments_list:
                    if attachment:
                        path = default_storage.save(f'pre_inspection/driver_reports/{attachment.name}', attachment)
                        attachment_paths.append(path)
                report.driver_report_attachments = attachment_paths
            
            report.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='PreInspectionReport',
                object_id=report.id,
                description=f'Updated pre-inspection report for {report.vehicle.plate_number} - {report.get_report_type_display()}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Pre-inspection report updated successfully!')
            return redirect('pre_inspection_detail', pk=report.pk)
    else:
        form = PreInspectionReportForm(instance=report)
    
    return render(request, 'core/pre_inspection_form.html', {'form': form, 'title': 'Edit Pre-Inspection Report', 'report': report})


@login_required
def pre_inspection_approve(request, pk):
    """Approve pre-inspection report"""
    report = get_object_or_404(PreInspectionReport, pk=pk)
    
    if request.method == 'POST':
        approval_notes = request.POST.get('approval_notes', '')
        report.approved_by = request.user
        report.approval_date = timezone.now()
        report.approval_notes = approval_notes
        report.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='approve',
            model_name='PreInspectionReport',
            object_id=report.id,
            description=f'Approved pre-inspection report for {report.vehicle.plate_number} - {report.get_report_type_display()}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'Pre-inspection report approved successfully!')
        return redirect('pre_inspection_detail', pk=report.pk)
    
    return render(request, 'core/pre_inspection_approve.html', {'report': report})


@login_required
def pre_inspection_delete(request, pk):
    """Delete pre-inspection report if it's not used"""
    report = get_object_or_404(PreInspectionReport, pk=pk)
    
    # Check if report is used
    repair_usage = Repair.objects.filter(pre_inspection=report).first()
    pms_usage = PMS.objects.filter(pre_inspection=report).first()
    
    if repair_usage or pms_usage:
        messages.error(
            request, 
            f'Cannot delete this pre-inspection report because it is already used by a {"repair" if repair_usage else "PMS"} record.'
        )
        return redirect('pre_inspection_detail', pk=pk)
    
    if request.method == 'POST':
        # Log activity before deletion
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='PreInspectionReport',
            object_id=report.id,
            description=f'Deleted pre-inspection report for {report.vehicle.plate_number} - {report.get_report_type_display()}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        report.delete()
        messages.success(request, 'Pre-inspection report deleted successfully!')
        return redirect('pre_inspection_list')
    
    return render(request, 'core/pre_inspection_delete.html', {'report': report})


@login_required
def post_inspection_list(request):
    """List all post-inspection reports"""
    reports = PostInspectionReport.objects.all().order_by('-inspection_date')
    
    # Get filter parameters
    availability_filter = request.GET.get('availability', '')
    vehicle_filter = request.GET.get('vehicle', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Apply filters
    if availability_filter == 'used':
        # Get IDs of reports used by repairs or PMS
        used_repair_ids = Repair.objects.exclude(post_inspection__isnull=True).values_list('post_inspection_id', flat=True)
        used_pms_ids = PMS.objects.exclude(post_inspection__isnull=True).values_list('post_inspection_id', flat=True)
        used_ids = set(list(used_repair_ids) + list(used_pms_ids))
        reports = reports.filter(id__in=used_ids)
    elif availability_filter == 'available':
        # Get IDs of reports used by repairs or PMS
        used_repair_ids = Repair.objects.exclude(post_inspection__isnull=True).values_list('post_inspection_id', flat=True)
        used_pms_ids = PMS.objects.exclude(post_inspection__isnull=True).values_list('post_inspection_id', flat=True)
        used_ids = set(list(used_repair_ids) + list(used_pms_ids))
        reports = reports.exclude(id__in=used_ids)
    
    if vehicle_filter:
        reports = reports.filter(vehicle_id=vehicle_filter)
    
    if date_from:
        try:
            from django.utils.dateparse import parse_datetime
            date_from_obj = parse_datetime(date_from) if 'T' in date_from else datetime.strptime(date_from, '%Y-%m-%d')
            if date_from_obj:
                reports = reports.filter(inspection_date__gte=date_from_obj)
        except (ValueError, TypeError):
            pass
    
    if date_to:
        try:
            from django.utils.dateparse import parse_datetime
            date_to_obj = parse_datetime(date_to) if 'T' in date_to else datetime.strptime(date_to, '%Y-%m-%d')
            if date_to_obj:
                # Add one day to include the full day
                from datetime import timedelta
                date_to_obj = date_to_obj + timedelta(days=1)
                reports = reports.filter(inspection_date__lt=date_to_obj)
        except (ValueError, TypeError):
            pass
    
    # Annotate each report with usage information
    for report in reports:
        # Check if used by a repair
        repair_usage = Repair.objects.filter(post_inspection=report).first()
        # Check if used by a PMS
        pms_usage = PMS.objects.filter(post_inspection=report).first()
        
        report.used_by_repair = repair_usage
        report.used_by_pms = pms_usage
        report.is_used = repair_usage is not None or pms_usage is not None
    
    # Get all vehicles for filter dropdown
    vehicles = Vehicle.objects.all().order_by('plate_number')
    
    context = {
        'reports': reports,
        'vehicles': vehicles,
        'availability_filter': availability_filter,
        'vehicle_filter': vehicle_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'core/post_inspection_list.html', context)


@login_required
def post_inspection_create(request):
    """Create a new post-inspection report"""
    if request.method == 'POST':
        form = PostInspectionReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            # Always set inspected_by to current user (or use form value if provided)
            if not report.inspected_by:
                report.inspected_by = request.user
            
            report.save()  # Save first to ensure we have an ID and can access vehicle
            
            # Handle multiple image uploads after initial save
            uploaded_images = request.FILES.getlist('replaced_parts_images')
            if uploaded_images:
                try:
                    from django.core.files.storage import default_storage
                    import os
                    from django.utils import timezone
                    image_paths = []
                    
                    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                    plate_number = report.vehicle.plate_number if report.vehicle else 'unknown'
                    
                    for idx, image in enumerate(uploaded_images):
                        # Generate unique filename
                        file_extension = os.path.splitext(image.name)[1] or '.jpg'
                        unique_filename = f"post_inspection/replaced_parts/{plate_number}_{timestamp}_{idx}{file_extension}"
                        
                        # Save the file
                        file_path = default_storage.save(unique_filename, image)
                        image_paths.append(file_path)
                    
                    # Store paths in JSONField
                    report.replaced_parts_images = image_paths
                    report.save()  # Save again with images
                except Exception as e:
                    # Log error but don't fail the entire save
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error saving replaced parts images: {str(e)}")
                    messages.warning(request, f'Some images could not be saved: {str(e)}')
            
            # If repair_id is provided in POST, link the report to the repair
            repair_id = request.POST.get('repair_id')
            if repair_id:
                try:
                    repair = Repair.objects.get(pk=repair_id)
                    repair.post_inspection = report
                    repair.save()
                except Repair.DoesNotExist:
                    pass
                except Exception as e:
                    # Handle validation errors gracefully
                    from django.core.exceptions import ValidationError
                    if isinstance(e, ValidationError):
                        messages.error(request, str(e))
                    else:
                        messages.error(request, f'Error linking post-inspection to repair: {str(e)}')
            
            # If pms_id is provided in POST, link the report to the PMS
            pms_id = request.POST.get('pms_id')
            if pms_id:
                try:
                    pms = PMS.objects.get(pk=pms_id)
                    pms.post_inspection = report
                    pms.save()
                except PMS.DoesNotExist:
                    pass
                except Exception as e:
                    # Handle validation errors gracefully
                    from django.core.exceptions import ValidationError
                    if isinstance(e, ValidationError):
                        messages.error(request, str(e))
                    else:
                        messages.error(request, f'Error linking post-inspection to PMS: {str(e)}')
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='create',
                model_name='PostInspectionReport',
                object_id=report.id,
                description=f'Created post-inspection report for {report.vehicle.plate_number} - {report.get_report_type_display()}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Post-inspection report created successfully!')
            return redirect('post_inspection_detail', pk=report.pk)
    else:
        form = PostInspectionReportForm()
        # Set default inspected_by to current user
        form.fields['inspected_by'].initial = request.user
        
        # Pre-populate form if repair_id is provided
        repair_id = request.GET.get('repair_id')
        if repair_id:
            try:
                repair = Repair.objects.get(pk=repair_id)
                form.fields['vehicle'].initial = repair.vehicle
                form.fields['report_type'].initial = 'repair'
                form.fields['pre_inspection'].initial = repair.pre_inspection
                # Filter pre-inspection to only show the repair's pre-inspection
                if repair.pre_inspection:
                    form.fields['pre_inspection'].queryset = PreInspectionReport.objects.filter(pk=repair.pre_inspection.pk)
            except Repair.DoesNotExist:
                pass
        
        # Pre-populate form if pms_id is provided
        pms_id = request.GET.get('pms_id')
        if pms_id:
            try:
                pms = PMS.objects.get(pk=pms_id)
                form.fields['vehicle'].initial = pms.vehicle
                form.fields['report_type'].initial = 'pms'
                form.fields['pre_inspection'].initial = pms.pre_inspection
                # Filter pre-inspection to only show the PMS's pre-inspection
                if pms.pre_inspection:
                    try:
                        form.fields['pre_inspection'].queryset = PreInspectionReport.objects.filter(pk=pms.pre_inspection.pk)
                    except PreInspectionReport.DoesNotExist:
                        # Pre-inspection was deleted, allow selecting any approved pre-inspection
                        form.fields['pre_inspection'].queryset = PreInspectionReport.objects.filter(is_approved=True)
                        form.fields['pre_inspection'].initial = None
            except PMS.DoesNotExist:
                pass
    
    return render(request, 'core/post_inspection_form.html', {'form': form, 'title': 'Create Post-Inspection Report'})


@login_required
def post_inspection_detail(request, pk):
    """View post-inspection report details"""
    report = get_object_or_404(PostInspectionReport, pk=pk)
    return render(request, 'core/post_inspection_detail.html', {'report': report})


@login_required
def post_inspection_edit(request, pk):
    """Edit post-inspection report"""
    report = get_object_or_404(PostInspectionReport, pk=pk)
    
    if request.method == 'POST':
        form = PostInspectionReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            # Save form data first (without replaced_parts_images since we handle it manually)
            report = form.save(commit=False)
            
            # Ensure inspected_by is always set
            # If editing, preserve existing inspected_by if it exists, otherwise use form value or current user
            if report.pk:
                # Get existing inspected_by from database
                existing_report = PostInspectionReport.objects.get(pk=report.pk)
                # Use existing value if form didn't provide one, otherwise use form value
                if not report.inspected_by:
                    report.inspected_by = existing_report.inspected_by or request.user
            else:
                # New record - use form value or current user
                if not report.inspected_by:
                    report.inspected_by = request.user
            
            # Handle multiple image uploads - append to existing images
            uploaded_images = request.FILES.getlist('replaced_parts_images')
            if uploaded_images:
                try:
                    from django.core.files.storage import default_storage
                    import os
                    
                    # Get existing images or initialize empty list
                    existing_images = report.get_replaced_parts_images_list()
                    
                    from django.utils import timezone
                    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                    plate_number = report.vehicle.plate_number if report.vehicle else 'unknown'
                    
                    for idx, image in enumerate(uploaded_images):
                        # Generate unique filename
                        file_extension = os.path.splitext(image.name)[1] or '.jpg'
                        unique_filename = f"post_inspection/replaced_parts/{plate_number}_{timestamp}_{len(existing_images) + idx}{file_extension}"
                        
                        # Save the file
                        file_path = default_storage.save(unique_filename, image)
                        existing_images.append(file_path)
                    
                    # Update the JSONField with all images
                    report.replaced_parts_images = existing_images
                except Exception as e:
                    # Log error but don't fail the entire save
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error saving replaced parts images: {str(e)}")
                    messages.warning(request, f'Some images could not be saved: {str(e)}')
            
            report.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='update',
                model_name='PostInspectionReport',
                object_id=report.id,
                description=f'Updated post-inspection report for {report.vehicle.plate_number} - {report.get_report_type_display()}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Post-inspection report updated successfully!')
            return redirect('post_inspection_detail', pk=report.pk)
    else:
        form = PostInspectionReportForm(instance=report)
    
    return render(request, 'core/post_inspection_form.html', {'form': form, 'title': 'Edit Post-Inspection Report', 'report': report})


@login_required
def post_inspection_approve(request, pk):
    """Approve post-inspection report"""
    report = get_object_or_404(PostInspectionReport, pk=pk)
    
    if request.method == 'POST':
        approval_notes = request.POST.get('approval_notes', '')
        report.approved_by = request.user
        report.approval_date = timezone.now()
        report.approval_notes = approval_notes
        report.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='approve',
            model_name='PostInspectionReport',
            object_id=report.id,
            description=f'Approved post-inspection report for {report.vehicle.plate_number} - {report.get_report_type_display()}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'Post-inspection report approved successfully!')
        return redirect('post_inspection_detail', pk=report.pk)
    
    return render(request, 'core/post_inspection_approve.html', {'report': report})


@login_required
def post_inspection_delete(request, pk):
    """Delete post-inspection report if it's not used"""
    report = get_object_or_404(PostInspectionReport, pk=pk)
    
    # Check if report is used
    repair_usage = Repair.objects.filter(post_inspection=report).first()
    pms_usage = PMS.objects.filter(post_inspection=report).first()
    
    if repair_usage or pms_usage:
        messages.error(
            request, 
            f'Cannot delete this post-inspection report because it is already used by a {"repair" if repair_usage else "PMS"} record.'
        )
        return redirect('post_inspection_detail', pk=pk)
    
    if request.method == 'POST':
        # Log activity before deletion
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            model_name='PostInspectionReport',
            object_id=report.id,
            description=f'Deleted post-inspection report for {report.vehicle.plate_number} - {report.get_report_type_display()}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        report.delete()
        messages.success(request, 'Post-inspection report deleted successfully!')
        return redirect('post_inspection_list')
    
    return render(request, 'core/post_inspection_delete.html', {'report': report})


@login_required
def system_manual(request):
    """Display system process flow and manual"""
    return render(request, 'core/system_manual.html')


@login_required
def repair_complete(request, pk):
    """Complete a repair after post-inspection is approved"""
    repair = get_object_or_404(Repair, pk=pk)
    
    # Check if repair can be completed
    if repair.status == 'Completed':
        messages.warning(request, 'This repair is already completed.')
        return redirect('repair_detail', pk=pk)
    
    if not repair.post_inspection:
        messages.error(request, 'Cannot complete repair without a post-inspection report.')
        return redirect('repair_detail', pk=pk)
    
    if not repair.post_inspection.is_approved:
        messages.error(request, 'Cannot complete repair without an approved post-inspection report.')
        return redirect('repair_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            repair.status = 'Completed'
            repair.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='complete',
                model_name='Repair',
                object_id=repair.id,
                description=f'Completed repair for {repair.vehicle.plate_number}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Repair for {repair.vehicle.plate_number} has been completed successfully!')
            return redirect('repair_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Error completing repair: {str(e)}')
    
    context = {
        'repair': repair,
        'post_inspection': repair.post_inspection,
    }
    return render(request, 'core/repair_complete.html', context)


@login_required
def pms_complete(request, pk):
    """Complete a PMS after post-inspection is approved"""
    pms = get_object_or_404(PMS, pk=pk)
    
    # Check if PMS can be completed
    if pms.status == 'Completed':
        messages.warning(request, 'This PMS is already completed.')
        return redirect('pms_detail', pk=pk)
    
    if not pms.post_inspection:
        messages.error(request, 'Cannot complete PMS without a post-inspection report.')
        return redirect('pms_detail', pk=pk)
    
    if not pms.post_inspection.is_approved:
        messages.error(request, 'Cannot complete PMS without an approved post-inspection report.')
        return redirect('pms_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            pms.status = 'Completed'
            pms.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='complete',
                model_name='PMS',
                object_id=pms.id,
                description=f'Completed PMS for {pms.vehicle.plate_number}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'PMS for {pms.vehicle.plate_number} has been completed successfully!')
            return redirect('pms_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Error completing PMS: {str(e)}')
    
    context = {
        'pms': pms,
        'post_inspection': pms.post_inspection,
    }
    return render(request, 'core/pms_complete.html', context)


@login_required
def get_pre_inspections_by_vehicle(request):
    """AJAX endpoint to get pre-inspection reports filtered by vehicle and report type"""
    vehicle_id = request.GET.get('vehicle_id')
    report_type = request.GET.get('report_type', 'repair')  # 'repair' or 'pms'
    
    if not vehicle_id:
        return JsonResponse({'error': 'vehicle_id is required'}, status=400)
    
    try:
        # Get used pre-inspection IDs
        used_pre_inspection_ids = set()
        
        # Get pre-inspections used by other repairs
        used_pre_inspection_ids.update(
            Repair.objects.exclude(pre_inspection__isnull=True)
                         .values_list('pre_inspection_id', flat=True)
        )
        
        # Get pre-inspections used by PMS
        used_pre_inspection_ids.update(
            PMS.objects.exclude(pre_inspection__isnull=True)
                      .values_list('pre_inspection_id', flat=True)
        )
        
        # Get available pre-inspections for the vehicle and report type
        pre_inspections = PreInspectionReport.objects.filter(
            vehicle_id=vehicle_id,
            report_type=report_type,
            approved_by__isnull=False
        ).exclude(id__in=used_pre_inspection_ids).order_by('-inspection_date')
        
        # Format as options for select dropdown
        options = [{'id': '', 'text': 'Select an approved pre-inspection report...'}]
        for inspection in pre_inspections:
            options.append({
                'id': inspection.id,
                'text': f"{inspection.vehicle.plate_number} - {inspection.inspection_date.strftime('%Y-%m-%d')}"
            })
        
        return JsonResponse({'options': options}, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)