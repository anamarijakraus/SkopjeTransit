from django.db import migrations

def update_bus_stops(apps, schema_editor):
    # Get the models
    Bus = apps.get_model('rides', 'Bus')
    Stop = apps.get_model('rides', 'Stop')
    BusSchedule = apps.get_model('rides', 'BusSchedule')
    
    # Clear existing data
    BusSchedule.objects.all().delete()
    Bus.objects.all().delete()
    Stop.objects.all().delete()
    
    # Define new bus lines with their exact stops (matching views.py)
    bus_lines = {
        '2': [
            "Gjorce Petrov Cinema", "Gjorce Petrov Old Market", "Vlae Porta", "Vlae", "Dolno Nerezi",
            "Skopje City Archives", "Karposh 3 Gas Station", "Bucharest Polyclinic", "Karposh 2", 
            "Mal Odmor", "Bunjakovec Shopping Center", "Posta Telecom", "Most Goce Delchev Theater", 
            "Bitpazar 2 Shopping Center", "Primary School Bitola Congress", "Hotel Continental"
        ],
        '4': [
            "Gjorce Petrov Cinema", "Gjorce Petrov Old Market", "Vlae Porta", "Vlae", "Dolno Nerezi", 
            "Skopje City Archives", "Karposh 3 Gas Station", "Bucharest Polyclinic", "Karposh 2", 
            "Mal Odmor", "Bunjakovec Shopping Center", "Bunjakovec Porta", "Centar Record", 
            "Zelen Pazar", "Bilna Apteka", "Cheshma Kisela Voda Maxi"
        ],
        '7': [
            "Karposh 3 TC City Mall T", "Restaurant Imes", "Primary School Lazo Trpovski", 
            "Hospital 8mi Septemvri", "Karposh 2", "Mal Odmor", "Bunjakovec Shopping Center", 
            "Bunjakovec Porta", "Centar Record", "Zelen Pazar", "Jugodrvo Olympic Pool", 
            "Vero Jambo", "Intercity Bus", "Tobacco Factory", "Dimitar Vlahov Secondary School", 
            "Rade Koncar Petrol Station"
        ],
        '15': [
            "Karposh 4 TC City Mall T", "Restaurant Imes", "Primary School Lazo Trpovski", 
            "Hospital 8mi Septemvri", "Karposh 2", "Mal Odmor", "Bunjakovec Shopping Center", 
            "Bunjakovec Porta", "Centar Record", "Zelen Pazar", "Jugodrvo Olympic Pool", 
            "Vero Jambo", "Railway Station", "TC Skopjanka", "Aerodrom Tobacco 2", "TC Tri Biseri"
        ],
        '19': [
            "Karposh 4 TC City Mall T", "Restaurant Imes", "Primary School Lazo Trpovski", 
            "Hospital 8mi Septemvri", "Karposh 2", "Mal Odmor", "Bunjakovec Shopping Center", 
            "Bunjakovec Porta", "Posta Telecom", "Most Goce Delchev Theater", 
            "Bitpazar 1 University of St. Cyril and Methodius", "Yaja Pasha Mosque", 
            "Chair", "Chair Buildings", "Chair Polyclinic", "Church of St. Nicholas"
        ],
        '22': [
            "Gjorce Petrov Polyclinic", "Vlae Porta", "Vlae", "Dolno Nerezi", "Skopje City Archives", 
            "Karposh 3 Gas Station", "Bucharest Polyclinic", "Karposh 2", "Mal Odmor", 
            "Bunjakovec Shopping Center", "Bunjakovec Porta", "Centar Record", "Zelen Pazar", 
            "Jugodrvo Olympic Pool", "Vero Jambo", "Intercity Bus"
        ],
        '24': [
            "Taftalidze T", "Taftalidze Market", "Skopje City Archives", "Karposh 3 Gas Station", 
            "Bucharest Polyclinic", "Karposh 2", "Mal Odmor", "Bunjakovec Shopping Center", 
            "Bunjakovec Porta", "Centar Record", "Zelen Pazar", "Kuzman Josifoski Pitu Primary School", 
            "Championche", "Kisela Voda Przino", "Home For The Blind", "Krume Kepeski Primary School"
        ],
        '60': [
            "Gjorce Petrov Cinema", "Gjorce Petrov Old Market", "Vlae Porta", "Vlae", "Dolno Nerezi", 
            "Skopje City Archives", "Karposh 3 Gas Station", "Bucharest Polyclinic", "Karposh 2", 
            "Mal Odmor", "Bunjakovec Shopping Center", "Posta Telecom", "Most Goce Delchev Theater", 
            "National University Library", "Vero Jambo", "Transporten Center T"
        ]
    }
    
    # Create all stops
    all_stops = set()
    for stops in bus_lines.values():
        all_stops.update(stops)
    
    for stop_name in all_stops:
        Stop.objects.get_or_create(name=stop_name)
    
    # Create buses and schedules
    from datetime import datetime, time, timedelta, date
    
    DAY_START = time(0, 0)  # Midnight
    MINUTES_PER_STOP = 6
    TOTAL_MINUTES_PER_DAY = 1440  # 24 hours
    
    for line_number, stops in bus_lines.items():
        bus, created = Bus.objects.get_or_create(name=f"Bus {line_number}")
        stops_count = len(stops)
        ROUTE_DURATION = MINUTES_PER_STOP * stops_count
        
        # Calculate how many full routes fit in a day
        full_routes_per_day = TOTAL_MINUTES_PER_DAY // ROUTE_DURATION
        
        # Calculate start times for each route
        for route_num in range(full_routes_per_day):
            route_start = datetime.combine(date.today(), DAY_START) + timedelta(minutes=route_num * ROUTE_DURATION)
            
            # Create schedule for each stop in this route
            for stop_num, stop_name in enumerate(stops):
                stop = Stop.objects.get(name=stop_name)
                arrival_time = (route_start + timedelta(minutes=stop_num * MINUTES_PER_STOP)).time()
                
                BusSchedule.objects.get_or_create(
                    bus=bus,
                    stop=stop,
                    arrival_time=arrival_time
                )

def reverse_update_bus_stops(apps, schema_editor):
    # This migration can't be reversed easily, so we'll just pass
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('rides', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_bus_stops, reverse_update_bus_stops),
    ] 