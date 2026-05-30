from django.db import migrations


def add_return_schedules(apps, schema_editor):
    import sys
    if 'test' in sys.argv:
        return

    Bus = apps.get_model('rides', 'Bus')
    Stop = apps.get_model('rides', 'Stop')
    BusSchedule = apps.get_model('rides', 'BusSchedule')

    from datetime import datetime, time, timedelta, date

    DAY_START = time(0, 0)
    MINUTES_PER_STOP = 6
    TOTAL_MINUTES = 1440

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

    for line_number, stops in bus_lines.items():
        try:
            bus = Bus.objects.get(name=f"Bus {line_number}")
        except Bus.DoesNotExist:
            continue

        stops_count = len(stops)
        route_duration = MINUTES_PER_STOP * stops_count
        half_offset = route_duration // 2
        full_routes_per_day = TOTAL_MINUTES // route_duration
        reversed_stops = list(reversed(stops))

        for route_num in range(full_routes_per_day):
            start_minutes = route_num * route_duration + half_offset
            if start_minutes >= TOTAL_MINUTES:
                continue
            route_start = datetime.combine(date.today(), DAY_START) + timedelta(minutes=start_minutes)

            for stop_num, stop_name in enumerate(reversed_stops):
                arrival_dt = route_start + timedelta(minutes=stop_num * MINUTES_PER_STOP)
                # Wrap past midnight back into the same day
                arrival_minutes = (start_minutes + stop_num * MINUTES_PER_STOP) % TOTAL_MINUTES
                arrival_time = (datetime.combine(date.today(), DAY_START) + timedelta(minutes=arrival_minutes)).time()

                try:
                    stop = Stop.objects.get(name=stop_name)
                except Stop.DoesNotExist:
                    continue

                BusSchedule.objects.get_or_create(bus=bus, stop=stop, arrival_time=arrival_time)


def reverse_add_return_schedules(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('rides', '0010_transaction'),
        ('rides', '0008_merge_0002_update_bus_stops_0007_bus_busschedule'),
    ]

    operations = [
        migrations.RunPython(add_return_schedules, reverse_add_return_schedules),
    ]
