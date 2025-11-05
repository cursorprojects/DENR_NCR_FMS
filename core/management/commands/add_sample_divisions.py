from django.core.management.base import BaseCommand
from core.models import Division


class Command(BaseCommand):
    help = 'Add sample division data'

    def handle(self, *args, **options):
        self.stdout.write('Adding sample division data...')
        
        # Sample divisions data
        divisions_data = [
            {
                'name': 'Administrative Division',
                'description': 'Handles administrative functions and office management'
            },
            {
                'name': 'Operations Division',
                'description': 'Manages daily operational activities and field work'
            },
            {
                'name': 'Technical Division',
                'description': 'Handles technical and engineering tasks'
            },
            {
                'name': 'Planning and Development Division',
                'description': 'Focuses on strategic planning and project development'
            },
            {
                'name': 'Finance Division',
                'description': 'Manages financial operations and budgeting'
            },
            {
                'name': 'Legal Division',
                'description': 'Handles legal matters and compliance'
            },
            {
                'name': 'Information Technology Division',
                'description': 'Manages IT infrastructure and systems'
            },
            {
                'name': 'Human Resources Division',
                'description': 'Handles personnel management and recruitment'
            },
            {
                'name': 'Environmental Division',
                'description': 'Focuses on environmental protection and compliance'
            },
            {
                'name': 'Research and Development Division',
                'description': 'Conducts research and development activities'
            }
        ]
        
        # Create divisions
        created_divisions = []
        for division_data in divisions_data:
            division, created = Division.objects.get_or_create(
                name=division_data['name'],
                defaults=division_data
            )
            if created:
                created_divisions.append(division)
                self.stdout.write(f'Created division: {division.name}')
            else:
                self.stdout.write(f'Division already exists: {division.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully added {len(created_divisions)} new divisions!'
            )
        )
        
        # Display summary
        total_divisions = Division.objects.count()
        self.stdout.write(f'\nTotal divisions in database: {total_divisions}')

