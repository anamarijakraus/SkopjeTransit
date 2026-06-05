from django.db import migrations


def fix_karposh_and_returns(apps, schema_editor):
    import sys
    if 'test' in sys.argv:
        return

    Stop = apps.get_model('rides', 'Stop')
    Bus = apps.get_model('rides', 'Bus')
    BusSchedule = apps.get_model('rides', 'BusSchedule')

    # Rename the stop
    try:
        stop = Stop.objects.get(name='Karposh 4 TC City Mall T')
        stop.name = 'Karposh 3 TC City Mall T'
        stop.save()
    except Stop.DoesNotExist:
        pass  # Already renamed or doesn't exist

    # Add the return-route entries that 0011 missed for buses 7, 15, 19
    # (0011 looked for "Karposh 3 TC City Mall T" which didn't exist yet)
    from datetime import datetime, time, timedelta, date

    DAY_START = time(0, 0)
    MINUTES_PER_STOP = 6
    TOTAL_MINUTES = 1440

    affected_lines = {
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
    }

    for line_number, stops in affected_lines.items():
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

            for stop_num, stop_name in enumerate(reversed_stops):
                arrival_minutes = (start_minutes + stop_num * MINUTES_PER_STOP) % TOTAL_MINUTES
                arrival_time = (
                    datetime.combine(date.today(), DAY_START) + timedelta(minutes=arrival_minutes)
                ).time()

                try:
                    stop_obj = Stop.objects.get(name=stop_name)
                except Stop.DoesNotExist:
                    continue

                BusSchedule.objects.get_or_create(bus=bus, stop=stop_obj, arrival_time=arrival_time)


def reverse_fix(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('rides', '0011_add_return_bus_schedules'),
    ]

    operations = [
        migrations.RunPython(fix_karposh_and_returns, reverse_fix),
    ]
