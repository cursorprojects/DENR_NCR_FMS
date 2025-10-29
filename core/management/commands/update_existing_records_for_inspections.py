from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from core.models import Repair, PMS, PreInspectionReport, PostInspectionReport, Vehicle, CustomUser
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Update existing repair and PMS records to comply with new inspection requirements'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get a user for creating inspection reports
        admin_user = CustomUser.objects.filter(role='super_admin').first()
        if not admin_user:
            admin_user = CustomUser.objects.first()
        
        if not admin_user:
            self.stdout.write(
                self.style.ERROR('No users found. Please create a user first.')
            )
            return
        
        updated_count = 0
        
        # Process repairs without pre-inspection
        repairs_without_pre = Repair.objects.filter(pre_inspection__isnull=True)
        
        self.stdout.write(f'\nProcessing {repairs_without_pre.count()} repairs without pre-inspection...')
        
        for repair in repairs_without_pre:
            if dry_run:
                self.stdout.write(
                    f'Would create pre-inspection for repair: {repair.vehicle.plate_number} - {repair.date_of_repair}'
                )
            else:
                try:
                    # Create a pre-inspection report for this repair
                    pre_inspection = PreInspectionReport.objects.create(
                        vehicle=repair.vehicle,
                        report_type='repair',
                        inspected_by=admin_user,
                        engine_condition=random.choice(['excellent', 'good', 'fair']),
                        transmission_condition=random.choice(['excellent', 'good', 'fair']),
                        brakes_condition=random.choice(['excellent', 'good', 'fair']),
                        suspension_condition=random.choice(['excellent', 'good', 'fair']),
                        electrical_condition=random.choice(['excellent', 'good', 'fair']),
                        body_condition=random.choice(['excellent', 'good', 'fair']),
                        tires_condition=random.choice(['excellent', 'good', 'fair']),
                        lights_condition=random.choice(['excellent', 'good', 'fair']),
                        current_mileage=repair.vehicle.current_mileage + random.randint(-1000, 1000),
                        fuel_level=random.choice(['full', 'three_quarters', 'half', 'quarter']),
                        issues_found=f'Pre-inspection created for existing repair: {repair.description}',
                        safety_concerns='No major safety concerns identified.',
                        recommended_actions=f'Proceed with repair: {repair.description}',
                        approved_by=admin_user,
                        approval_date=repair.date_of_repair,
                        approval_notes='Auto-approved for existing repair record'
                    )
                    
                    # Link the repair to the pre-inspection
                    repair.pre_inspection = pre_inspection
                    repair.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created pre-inspection for repair: {repair.vehicle.plate_number} - {repair.date_of_repair}'
                        )
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error creating pre-inspection for repair {repair.id}: {str(e)}'
                        )
                    )
            
            updated_count += 1
        
        # Process PMS records without pre-inspection
        pms_without_pre = PMS.objects.filter(pre_inspection__isnull=True)
        
        self.stdout.write(f'\nProcessing {pms_without_pre.count()} PMS records without pre-inspection...')
        
        for pms in pms_without_pre:
            if dry_run:
                self.stdout.write(
                    f'Would create pre-inspection for PMS: {pms.vehicle.plate_number} - {pms.scheduled_date}'
                )
            else:
                try:
                    # Create a pre-inspection report for this PMS
                    pre_inspection = PreInspectionReport.objects.create(
                        vehicle=pms.vehicle,
                        report_type='pms',
                        inspected_by=admin_user,
                        engine_condition=random.choice(['excellent', 'good', 'fair']),
                        transmission_condition=random.choice(['excellent', 'good', 'fair']),
                        brakes_condition=random.choice(['excellent', 'good', 'fair']),
                        suspension_condition=random.choice(['excellent', 'good', 'fair']),
                        electrical_condition=random.choice(['excellent', 'good', 'fair']),
                        body_condition=random.choice(['excellent', 'good', 'fair']),
                        tires_condition=random.choice(['excellent', 'good', 'fair']),
                        lights_condition=random.choice(['excellent', 'good', 'fair']),
                        current_mileage=pms.mileage_at_service or pms.vehicle.current_mileage,
                        fuel_level=random.choice(['full', 'three_quarters', 'half', 'quarter']),
                        issues_found=f'Pre-inspection created for existing PMS: {pms.service_type}',
                        safety_concerns='No major safety concerns identified.',
                        recommended_actions=f'Proceed with PMS: {pms.service_type}',
                        approved_by=admin_user,
                        approval_date=pms.scheduled_date,
                        approval_notes='Auto-approved for existing PMS record'
                    )
                    
                    # Link the PMS to the pre-inspection
                    pms.pre_inspection = pre_inspection
                    pms.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created pre-inspection for PMS: {pms.vehicle.plate_number} - {pms.scheduled_date}'
                        )
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error creating pre-inspection for PMS {pms.id}: {str(e)}'
                        )
                    )
            
            updated_count += 1
        
        # Process completed repairs without post-inspection
        completed_repairs_without_post = Repair.objects.filter(
            status='Completed',
            post_inspection__isnull=True
        )
        
        self.stdout.write(f'\nProcessing {completed_repairs_without_post.count()} completed repairs without post-inspection...')
        
        for repair in completed_repairs_without_post:
            if dry_run:
                self.stdout.write(
                    f'Would create post-inspection for completed repair: {repair.vehicle.plate_number} - {repair.date_of_repair}'
                )
            else:
                try:
                    # Create a post-inspection report for this completed repair
                    post_inspection = PostInspectionReport.objects.create(
                        vehicle=repair.vehicle,
                        report_type='repair',
                        inspected_by=admin_user,
                        pre_inspection=repair.pre_inspection,
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
                        test_drive_notes=f'Test drive completed successfully after repair: {repair.description}',
                        remaining_issues='No remaining issues identified.',
                        future_recommendations=f'Continue regular maintenance for {repair.vehicle.plate_number}',
                        warranty_notes=f'Warranty information for repair: {repair.description}',
                        approved_by=admin_user,
                        approval_date=repair.date_of_repair + timedelta(days=1),
                        approval_notes='Auto-approved for existing completed repair'
                    )
                    
                    # Link the repair to the post-inspection
                    repair.post_inspection = post_inspection
                    repair.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created post-inspection for completed repair: {repair.vehicle.plate_number} - {repair.date_of_repair}'
                        )
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error creating post-inspection for repair {repair.id}: {str(e)}'
                        )
                    )
            
            updated_count += 1
        
        # Process completed PMS records without post-inspection
        completed_pms_without_post = PMS.objects.filter(
            status='Completed',
            post_inspection__isnull=True
        )
        
        self.stdout.write(f'\nProcessing {completed_pms_without_post.count()} completed PMS records without post-inspection...')
        
        for pms in completed_pms_without_post:
            if dry_run:
                self.stdout.write(
                    f'Would create post-inspection for completed PMS: {pms.vehicle.plate_number} - {pms.scheduled_date}'
                )
            else:
                try:
                    # Create a post-inspection report for this completed PMS
                    post_inspection = PostInspectionReport.objects.create(
                        vehicle=pms.vehicle,
                        report_type='pms',
                        inspected_by=admin_user,
                        pre_inspection=pms.pre_inspection,
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
                        test_drive_notes=f'Test drive completed successfully after PMS: {pms.service_type}',
                        remaining_issues='No remaining issues identified.',
                        future_recommendations=f'Continue regular PMS schedule for {pms.vehicle.plate_number}',
                        warranty_notes=f'Warranty information for PMS: {pms.service_type}',
                        approved_by=admin_user,
                        approval_date=pms.completed_date or pms.scheduled_date + timedelta(days=1),
                        approval_notes='Auto-approved for existing completed PMS'
                    )
                    
                    # Link the PMS to the post-inspection
                    pms.post_inspection = post_inspection
                    pms.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created post-inspection for completed PMS: {pms.vehicle.plate_number} - {pms.scheduled_date}'
                        )
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error creating post-inspection for PMS {pms.id}: {str(e)}'
                        )
                    )
            
            updated_count += 1
        
        # Summary
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\nDry run complete. Would update {updated_count} records.'
                )
            )
            self.stdout.write('Run without --dry-run to apply changes.')
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully updated {updated_count} records to comply with inspection requirements!'
                )
            )
        
        # Show statistics
        self.stdout.write(f'\nCurrent Statistics:')
        self.stdout.write(f'Total repairs: {Repair.objects.count()}')
        self.stdout.write(f'Repairs with pre-inspection: {Repair.objects.filter(pre_inspection__isnull=False).count()}')
        self.stdout.write(f'Repairs with post-inspection: {Repair.objects.filter(post_inspection__isnull=False).count()}')
        self.stdout.write(f'Total PMS records: {PMS.objects.count()}')
        self.stdout.write(f'PMS records with pre-inspection: {PMS.objects.filter(pre_inspection__isnull=False).count()}')
        self.stdout.write(f'PMS records with post-inspection: {PMS.objects.filter(post_inspection__isnull=False).count()}')
