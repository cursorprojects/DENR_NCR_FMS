from django.core.management.base import BaseCommand
from core.models import RepairPart


class Command(BaseCommand):
    help = 'Add common car repair parts to the database'

    def handle(self, *args, **kwargs):
        parts = [
            # Engine Parts
            {'name': 'Engine Oil', 'description': 'Motor oil for engine lubrication'},
            {'name': 'Oil Filter', 'description': 'Oil filter replacement'},
            {'name': 'Air Filter', 'description': 'Engine air filter'},
            {'name': 'Cabin Air Filter', 'description': 'Air conditioning air filter'},
            {'name': 'Fuel Filter', 'description': 'Fuel system filter'},
            {'name': 'Spark Plugs', 'description': 'Engine ignition spark plugs'},
            {'name': 'Water Pump', 'description': 'Engine cooling system water pump'},
            {'name': 'Radiator', 'description': 'Engine cooling radiator'},
            {'name': 'Thermostat', 'description': 'Engine cooling thermostat'},
            {'name': 'Fan Belt', 'description': 'Engine fan belt'},
            {'name': 'Serpentine Belt', 'description': 'Multi-component drive belt'},
            {'name': 'Timing Belt', 'description': 'Engine timing belt'},
            {'name': 'Alternator', 'description': 'Battery charging alternator'},
            {'name': 'Starter Motor', 'description': 'Engine starter motor'},
            {'name': 'Fuel Pump', 'description': 'Fuel delivery pump'},
            
            # Transmission
            {'name': 'Transmission Fluid', 'description': 'Automatic/Manual transmission fluid'},
            {'name': 'Clutch', 'description': 'Manual transmission clutch'},
            {'name': 'Clutch Disc', 'description': 'Clutch friction disc'},
            {'name': 'Flywheel', 'description': 'Engine flywheel'},
            
            # Brake System
            {'name': 'Brake Pads', 'description': 'Front brake pads'},
            {'name': 'Brake Shoes', 'description': 'Rear drum brake shoes'},
            {'name': 'Brake Discs/Rotors', 'description': 'Brake rotors'},
            {'name': 'Brake Fluid', 'description': 'Hydraulic brake fluid'},
            {'name': 'Brake Calipers', 'description': 'Brake caliper units'},
            {'name': 'Brake Master Cylinder', 'description': 'Brake master cylinder'},
            
            # Electrical System
            {'name': 'Car Battery', 'description': 'Vehicle battery'},
            {'name': 'Battery Terminals', 'description': 'Battery connection terminals'},
            {'name': 'Headlight Bulbs', 'description': 'Front headlight bulbs'},
            {'name': 'Taillight Bulbs', 'description': 'Rear taillight bulbs'},
            {'name': 'Turn Signal Bulbs', 'description': 'Turn indicator bulbs'},
            {'name': 'Fog Light Bulbs', 'description': 'Fog light bulbs'},
            {'name': 'LED Lights', 'description': 'LED light replacements'},
            
            # Suspension & Steering
            {'name': 'Shock Absorbers', 'description': 'Shock absorber units'},
            {'name': 'Struts', 'description': 'Strut assembly'},
            {'name': 'Coil Springs', 'description': 'Suspension coil springs'},
            {'name': 'Ball Joints', 'description': 'Suspension ball joints'},
            {'name': 'Tie Rods', 'description': 'Steering tie rod ends'},
            {'name': 'Wheel Bearings', 'description': 'Wheel hub bearings'},
            {'name': 'Power Steering Fluid', 'description': 'Power steering hydraulic fluid'},
            
            # Wheels & Tires
            {'name': 'Tires', 'description': 'Vehicle tires replacement'},
            {'name': 'Wheel Alignment', 'description': 'Tire alignment service'},
            {'name': 'Tire Rotation', 'description': 'Tire rotation service'},
            {'name': 'Wheel Balance', 'description': 'Tire/wheel balancing'},
            
            # Exhaust System
            {'name': 'Muffler', 'description': 'Exhaust muffler'},
            {'name': 'Catalytic Converter', 'description': 'Emissions catalytic converter'},
            {'name': 'Exhaust Pipe', 'description': 'Exhaust system piping'},
            {'name': 'Exhaust Gasket', 'description': 'Exhaust connection gaskets'},
            
            # HVAC System
            {'name': 'A/C Compressor', 'description': 'Air conditioning compressor'},
            {'name': 'A/C Condenser', 'description': 'AC condenser unit'},
            {'name': 'A/C Refrigerant', 'description': 'Air conditioning gas'},
            {'name': 'Heater Core', 'description': 'Vehicle heating system core'},
            
            # Fluid Replacements
            {'name': 'Coolant/Antifreeze', 'description': 'Engine coolant'},
            {'name': 'Brake Fluid Replacement', 'description': 'Brake fluid service'},
            {'name': 'Transmission Fluid Change', 'description': 'Transmission fluid service'},
            {'name': 'Power Steering Fluid', 'description': 'Power steering fluid'},
            {'name': 'Differential Fluid', 'description': 'Rear axle differential oil'},
            
            # Wipers & Visibility
            {'name': 'Windshield Wiper Blades', 'description': 'Front wiper blades'},
            {'name': 'Rear Wiper Blade', 'description': 'Rear window wiper'},
            {'name': 'Windshield', 'description': 'Front windshield replacement'},
            {'name': 'Side Windows', 'description': 'Side window glass'},
            
            # Body & Trim
            {'name': 'Side Mirrors', 'description': 'Exterior side mirrors'},
            {'name': 'Bumper', 'description': 'Front/rear bumper'},
            {'name': 'Fender', 'description': 'Vehicle fender panel'},
            {'name': 'Door Handle', 'description': 'Exterior door handles'},
            
            # Filters & Fluids Maintenance
            {'name': 'PCV Valve', 'description': 'Positive crankcase ventilation valve'},
            {'name': 'PCV Hose', 'description': 'PCV system hoses'},
            {'name': 'Vacuum Hoses', 'description': 'Engine vacuum system hoses'},
            {'name': 'Radiator Hose', 'description': 'Cooling system hoses'},
            {'name': 'Heater Hose', 'description': 'Heating system hoses'},
            
            # Ignition System
            {'name': 'Ignition Coil', 'description': 'Engine ignition coil'},
            {'name': 'Distributor Cap', 'description': 'Ignition distributor cap'},
            {'name': 'Ignition Wires', 'description': 'Spark plug wires'},
            
            # Fuel System
            {'name': 'Fuel Injector', 'description': 'Fuel injector cleaning'},
            {'name': 'Throttle Body', 'description': 'Throttle body service'},
            {'name': 'Idle Air Control Valve', 'description': 'IAC valve replacement'},
            
            # Emissions
            {'name': 'EGR Valve', 'description': 'Exhaust gas recirculation valve'},
            {'name': 'Oxygen Sensor', 'description': 'O2 sensor'},
            {'name': 'Mass Air Flow Sensor', 'description': 'MAF sensor'},
            {'name': 'Crank Position Sensor', 'description': 'Crankshaft position sensor'},
            
            # Safety
            {'name': 'Airbag Module', 'description': 'Airbag system module'},
            {'name': 'Seatbelt', 'description': 'Safety seatbelt replacement'},
            {'name': 'ABS Sensor', 'description': 'Anti-lock brake sensor'},
            
            # Electronics
            {'name': 'ECU/ECM', 'description': 'Engine control unit'},
            {'name': 'BCM', 'description': 'Body control module'},
            {'name': 'Relays', 'description': 'Electrical relay switches'},
            {'name': 'Fuses', 'description': 'Electrical fuses'},
        ]
        
        created_count = 0
        for part_data in parts:
            part, created = RepairPart.objects.get_or_create(
                name=part_data['name'],
                defaults={
                    'description': part_data['description'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {part.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Already exists: {part.name}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully processed {len(parts)} parts. '
            f'Created {created_count} new parts.'
        ))

