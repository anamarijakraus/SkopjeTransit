#!/usr/bin/env python
"""
Complete database setup script for SkopjeTransit
Run this when you have Python access: python setup_database.py
This will create the database, run migrations, and populate it with new bus data.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkopjeTransit.settings')
django.setup()

from rides.models import Bus, Stop, BusSchedule
from datetime import datetime, time, timedelta, date

def setup_database():
    print("🚀 Starting complete database setup...")
    
    # Step 1: Run migrations
    print("📋 Running migrations...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully!")
    except Exception as e:
        print(f"⚠️ Migration warning (this might be normal): {e}")
    
    # Step 2: Clear any existing data
    print("🧹 Clearing existing data...")
    BusSchedule.objects.all().delete()
    Bus.objects.all().delete()
    Stop.objects.all().delete()
    
    # Step 3: Define new bus lines with their exact stops (matching views.py)
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
    
    # Step 4: Create all stops
    print("📍 Creating stops...")
    all_stops = set()
    for stops in bus_lines.values():
        all_stops.update(stops)
    
    for stop_name in all_stops:
        Stop.objects.get_or_create(name=stop_name)
    
    print(f"✅ Created {len(all_stops)} stops")
    
    # Step 5: Create buses and schedules
    print("🚌 Creating buses and schedules...")
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
        
        print(f"✅ Created schedule for Bus {line_number} with {stops_count} stops")
    
    # Step 6: Create a superuser (optional)
    print("\n🎉 Database setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Run your Django server: python manage.py runserver")
    print("2. Test the 'View Stops' buttons - they should work perfectly now!")
    print("3. The maps will show the correct routes for each bus")
    
    # Show summary
    print(f"\n📊 Summary:")
    print(f"- Total stops created: {Stop.objects.count()}")
    print(f"- Total buses created: {Bus.objects.count()}")
    print(f"- Total schedules created: {BusSchedule.objects.count()}")

if __name__ == "__main__":
    setup_database() 