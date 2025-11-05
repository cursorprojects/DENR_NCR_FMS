from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Vehicle, CustomUser, PreInspectionReport, PostInspectionReport, Repair, PMS
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Create sample inspection reports to demonstrate the new inspection system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of inspection report pairs to create (default: 5)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get vehicles and users
        vehicles = list(Vehicle.objects.all())
        users = list(CustomUser.objects.all())
        
        if not vehicles:
            self.stdout.write(
                self.style.ERROR('No vehicles found. Please add vehicles first.')
            )
            return
        
        if not users:
            self.stdout.write(
                self.style.ERROR('No users found. Please create users first.')
            )
            return
        
        # Select random vehicles
        selected_vehicles = random.sample(vehicles, min(count, len(vehicles)))
        
        created_reports = {
            'pre_inspections': 0,
            'post_inspections': 0,
            'repairs': 0,
            'pms': 0
        }
        
        for vehicle in selected_vehicles:
            self.stdout.write(f'\nProcessing vehicle: {vehicle.plate_number}')
            
            # Create pre-inspection report
            report_type = random.choice(['repair', 'pms'])
            
            pre_inspection = PreInspectionReport.objects.create(
                vehicle=vehicle,
                report_type=report_type,
                inspected_by=random.choice(users),
                engine_condition=random.choice(['excellent', 'good', 'fair']),
                transmission_condition=random.choice(['excellent', 'good', 'fair']),
                brakes_condition=random.choice(['excellent', 'good', 'fair']),
                suspension_condition=random.choice(['excellent', 'good', 'fair']),
                electrical_condition=random.choice(['excellent', 'good', 'fair']),
                body_condition=random.choice(['excellent', 'good', 'fair']),
                tires_condition=random.choice(['excellent', 'good', 'fair']),
                lights_condition=random.choice(['excellent', 'good', 'fair']),
                current_mileage=vehicle.current_mileage + random.randint(-1000, 1000),
                fuel_level=random.choice(['full', 'three_quarters', 'half', 'quarter']),
                issues_found=f'Sample issues found during pre-inspection for {vehicle.plate_number}:\n- Minor wear on brake pads\n- Small scratch on front bumper\n- Air filter needs replacement',
                safety_concerns='No major safety concerns identified.',
                recommended_actions=f'Recommended actions before {report_type}:\n- Replace air filter\n- Check brake fluid level\n- Clean vehicle interior',
                approved_by=random.choice(users),
                approval_date=timezone.now() - timedelta(days=random.randint(1, 7)),
                approval_notes=f'Pre-inspection approved for {report_type} work on {vehicle.plate_number}.'
            )
            created_reports['pre_inspections'] += 1
            
            self.stdout.write(f'  Created pre-inspection: {report_type} - {pre_inspection.overall_condition}')
            
            # Create corresponding repair or PMS record
            if report_type == 'repair':
                repair = Repair.objects.create(
                    vehicle=vehicle,
                    date_of_repair=timezone.now().date() - timedelta(days=random.randint(1, 5)),
                    description=f'Sample repair work for {vehicle.plate_number}',
                    cost=random.randint(2000, 8000),
                    labor_cost=random.randint(1000, 3000),
                    technician='Sample Technician',
                    status='Completed',
                    pre_inspection=pre_inspection
                )
                created_reports['repairs'] += 1
                
                self.stdout.write(f'  Created repair: {repair.status} - ${repair.total_cost}')
                
            else:  # PMS
                pms = PMS.objects.create(
                    vehicle=vehicle,
                    service_type='General Inspection',
                    scheduled_date=timezone.now().date() - timedelta(days=random.randint(1, 5)),
                    completed_date=timezone.now().date() - timedelta(days=random.randint(0, 2)),
                    mileage_at_service=vehicle.current_mileage + random.randint(-500, 500),
                    next_service_mileage=vehicle.current_mileage + random.randint(5000, 10000),
                    cost=random.randint(1000, 3000),
                    provider='Sample Service Center',
                    technician='Sample PMS Technician',
                    description=f'Sample PMS service for {vehicle.plate_number}',
                    notes='Sample PMS record for inspection demonstration',
                    status='Completed',
                    pre_inspection=pre_inspection
                )
                created_reports['pms'] += 1
                
                self.stdout.write(f'  Created PMS: {pms.status} - {pms.service_type}')
            
            # Create post-inspection report
            post_inspection = PostInspectionReport.objects.create(
                vehicle=vehicle,
                report_type=report_type,
                inspected_by=random.choice(users),
                pre_inspection=pre_inspection,
                work_completed_satisfactorily=True,
                quality_of_work=random.choice(['excellent', 'good', 'satisfactory']),
                timeliness=random.choice(['excellent', 'good', 'satisfactory']),
                cleanliness=random.choice(['excellent', 'good', 'satisfactory']),
                engine_condition=random.choice(['excellent', 'good']),
                transmission_condition=random.choice(['excellent', 'good']),
                brakes_condition=random.choice(['excellent', 'good']),
                suspension_condition=random.choice(['excellent', 'good']),
                electrical_condition=random.choice(['excellent', 'good']),
                body_condition=random.choice(['excellent', 'good']),
                tires_condition=random.choice(['excellent', 'good']),
                lights_condition=random.choice(['excellent', 'good']),
                test_drive_performed=True,
                test_drive_distance=random.randint(5, 20),
                test_drive_notes=f'Test drive completed successfully. Vehicle performed well during {random.randint(5, 20)}km test drive.',
                remaining_issues='No remaining issues identified.',
                future_recommendations=f'Future maintenance recommendations for {vehicle.plate_number}:\n- Schedule next service in 6 months\n- Monitor brake pad wear\n- Check tire pressure regularly',
                warranty_notes=f'Warranty information for {vehicle.plate_number}:\n- Parts warranty: 12 months\n- Labor warranty: 6 months',
                approved_by=random.choice(users),
                approval_date=timezone.now() - timedelta(days=random.randint(0, 3)),
                approval_notes=f'Post-inspection approved. {report_type.title()} work completed satisfactorily.'
            )
            created_reports['post_inspections'] += 1
            
            self.stdout.write(f'  Created post-inspection: {post_inspection.overall_condition} - {post_inspection.condition_improvement}')
            
            # Link post-inspection to repair/PMS
            if report_type == 'repair':
                repair.post_inspection = post_inspection
                repair.save()
            else:
                pms.post_inspection = post_inspection
                pms.save()
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSample inspection data creation complete!'
            )
        )
        self.stdout.write(f'Processed {len(selected_vehicles)} vehicles')
        self.stdout.write(f'Created {created_reports["pre_inspections"]} pre-inspection reports')
        self.stdout.write(f'Created {created_reports["post_inspections"]} post-inspection reports')
        self.stdout.write(f'Created {created_reports["repairs"]} repair records')
        self.stdout.write(f'Created {created_reports["pms"]} PMS records')
        
        self.stdout.write(
            self.style.SUCCESS(
                '\nYou can now test the inspection report features:'
            )
        )
        self.stdout.write('  - View pre-inspection reports at /pre-inspections/')
        self.stdout.write('  - View post-inspection reports at /post-inspections/')
        self.stdout.write('  - Test the approval workflow for inspection reports')
        self.stdout.write('  - See how inspection reports link to repairs and PMS records')
        self.stdout.write('  - Observe condition improvement tracking')
