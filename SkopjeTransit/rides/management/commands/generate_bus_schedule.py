from django.core.management.base import BaseCommand
from datetime import datetime, time, timedelta, date

from rides.models import Bus, Stop, BusSchedule  # Make sure this imports your actual models


class Command(BaseCommand):
    help = 'Generates 24/7 bus schedules for all routes'

    def handle(self, *args, **options):
        # Define all bus lines with their exact stops
        bus_lines = {
            '2': [
                "Saraj", "Gjorce Petrov Makpetrol", "Gjorce Petrov Municipality", "Gjorce Petrov Market",
                "Vlae Porta", "Vlae", "TC City Mall", "Karposh 3 Gas Station", "Hotel Karposh",
                "Simpo", "Faculty of Civil Engineering", "Cathedral Temple", "Post Office City Wall",
                "Goce Delchev Bridge", "Bitpazar", "Municipality of Gazi Baba"
            ],
            '4': [
                "Gjorce Petrov Makpetrol", "Gjorce Petrov Municipality", "Gjorce Petrov Market",
                "Vlae Porta", "Vlae", "TC City Mall", "Karposh 3 Gas Station", "Hotel Karposh",
                "Simpo", "Faculty of Civil Engineering", "Cathedral Temple", "Record",
                "City Hospital", "Insurance Macedonia", "Municipality of Kisela Voda", "11 October"
            ],
            '7': [
                "Karposh 3 TC City Mall", "Karposh 3 Gas Station", "Hotel Karposh", "Simpo",
                "Faculty of Civil Engineering", "Cathedral Temple", "Record", "City Hospital",
                "Jugodrvo", "Bank of Rm 1", "Transport Center", "Intercity Bus",
                "Tobacco Factory", "Municipality of Aerodrom", "Rade Končar", "American College"
            ],
            '15': [
                "TC City Mall", "Karposh 3 Gas Station", "Hotel Karposh", "Simpo",
                "Faculty of Civil Engineering", "Cathedral Temple", "Record", "City Hospital",
                "Jugodrvo", "Bank of Rm 1", "Transport Center", "Skopjanka Mall",
                "Palma Airport", "Tri Biseri Mall", "Capitol Mall", "Novo Lisice"
            ],
            '19': [
                "Gjorce Petrov Makpetrol", "Gjorce Petrov Municipality", "Gjorce Petrov Market",
                "Vlae Porta", "Vlae", "TC City Mall", "Karposh 3 Gas Station", "Hotel Karposh",
                "Simpo", "Faculty of Civil Engineering", "Cathedral Temple", "Post Office City Wall",
                "Gotse Delchev Bridge", "Bitpazar", "Chair", "Chair Polyclinic"
            ],
            '22': [
                "Gjorce Petrov Makpetrol", "Gjorce Petrov Municipality", "Gjorce Petrov Market",
                "Vlae Porta", "Vlae", "TC City Mall", "Karposh 3 Gas Station", "Hotel Karposh",
                "Simpo", "Faculty of Civil Engineering", "Cathedral Temple", "Record",
                "City Hospital", "Jugodrvo", "Bank of Rm 1", "Transport Center"
            ],
            '24': [
                "Taftalidze T", "Taftalidze Market", "Karposh 3 Gas Station", "Hotel Karposh",
                "Simpo", "Faculty of Civil Engineering", "Cathedral Temple", "Record",
                "City Hospital", "Kuzman Josifoski Elementary School", "Championche",
                "Kisela Voda Zito Market", "Home for the Blind", "Mirka Factory", "Kisela Voda T", "Pripor"
            ],
            '60': [
                "Saraj", "Gjorce Petrov Makpetrol", "Gjorce Petrov Municipality", "Gjorce Petrov Market",
                "Vlae Porta", "Vlae", "TC City Mall", "Karposh 3 Gas Station", "Hotel Karposh",
                "Simpo", "Faculty of Civil Engineering", "Cathedral Temple", "City Wall Post Office",
                "Goce Delchev Bridge", "Bank of Rm 2", "Transport Center"
            ]
        }

        # First ensure all stops exist
        all_stops = set()
        for stops in bus_lines.values():
            all_stops.update(stops)

        for stop_name in all_stops:
            Stop.objects.get_or_create(name=stop_name)

        # Constants
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

            self.stdout.write(self.style.SUCCESS(f'Created schedule for Bus {line_number} with {stops_count} stops'))

        self.stdout.write(self.style.SUCCESS('All bus schedules created successfully!'))