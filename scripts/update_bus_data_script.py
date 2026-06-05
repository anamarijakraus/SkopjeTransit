#!/usr/bin/env python
"""
Simple script to update bus data with new stops from views.py
Run from the project root: python scripts/update_bus_data_script.py
"""

import os
import sys
import django

# Add the project root (one level up from this script) to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkopjeTransit.settings')
django.setup()

from rides.models import Bus, Stop, BusSchedule
from datetime import datetime, time, timedelta, date

def update_bus_data():
    print("Starting bus data update...")

    # Clear existing data
    print("Clearing existing data...")
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
            "Karposh 3 TC City Mall T", "Restaurant Imes", "Primary School Lazo Trpovski",
            "Hospital 8mi Septemvri", "Karposh 2", "Mal Odmor", "Bunjakovec Shopping Center",
            "Bunjakovec Porta", "Centar Record", "Zelen Pazar", "Jugodrvo Olympic Pool",
            "Vero Jambo", "Railway Station", "TC Skopjanka", "Aerodrom Tobacco 2", "TC Tri Biseri"
        ],
        '19': [
            "Karposh 3 TC City Mall T", "Restaurant Imes", "Primary School Lazo Trpovski",
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

    # Create all stops in route-flow order
    print("Creating stops...")
    STOP_ORDER = [
        "Gjorce Petrov Polyclinic", "Gjorce Petrov Cinema", "Gjorce Petrov Old Market",
        "Vlae Porta", "Vlae", "Dolno Nerezi", "Skopje City Archives", "Karposh 3 Gas Station",
        "Bucharest Polyclinic", "Taftalidze T", "Taftalidze Market", "Karposh 3 TC City Mall T",
        "Restaurant Imes", "Primary School Lazo Trpovski", "Hospital 8mi Septemvri", "Karposh 2",
        "Mal Odmor", "Bunjakovec Shopping Center", "Bunjakovec Porta", "Centar Record",
        "Zelen Pazar", "Kuzman Josifoski Pitu Primary School", "Championche", "Kisela Voda Przino",
        "Home For The Blind", "Krume Kepeski Primary School", "Bilna Apteka", "Cheshma Kisela Voda Maxi",
        "Jugodrvo Olympic Pool", "Vero Jambo", "Railway Station", "Intercity Bus", "Tobacco Factory",
        "Dimitar Vlahov Secondary School", "Rade Koncar Petrol Station", "Transporten Center T",
        "TC Skopjanka", "Aerodrom Tobacco 2", "TC Tri Biseri", "Posta Telecom",
        "Most Goce Delchev Theater", "National University Library",
        "Bitpazar 1 University of St. Cyril and Methodius", "Yaja Pasha Mosque",
        "Chair", "Chair Buildings", "Chair Polyclinic", "Church of St. Nicholas",
        "Bitpazar 2 Shopping Center", "Primary School Bitola Congress", "Hotel Continental",
    ]
    for i, stop_name in enumerate(STOP_ORDER):
        Stop.objects.get_or_create(name=stop_name, defaults={'order': i})

    print(f"Created {len(STOP_ORDER)} stops")

    # Create buses and schedules
    print("Creating buses and schedules...")
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

        print(f"Created schedule for Bus {line_number} with {stops_count} stops")

    print("Bus data update completed successfully!")

if __name__ == "__main__":
    update_bus_data()
