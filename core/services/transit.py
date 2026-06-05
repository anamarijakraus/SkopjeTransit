from rides.models import Stop, Bus, BusSchedule, Ride, Booking
from django.utils import timezone
from datetime import datetime


def get_all_stop_names() -> list:
    return sorted(Stop.objects.values_list('name', flat=True))


def find_matching_stops(query: str) -> list:
    if len(query.strip()) < 2:
        return []
    # Exact match wins — avoids ambiguity when one stop name is a substring of another
    exact = list(Stop.objects.filter(name__iexact=query).values_list('name', flat=True))
    if exact:
        return exact
    return sorted(Stop.objects.filter(name__icontains=query).values_list('name', flat=True).distinct())


def find_stop(name: str):
    try:
        return Stop.objects.get(name__iexact=name)
    except Stop.DoesNotExist:
        return None


def can_serve(ride, pickup_name: str, dropoff_name: str) -> bool:
    pn = pickup_name.strip().lower()
    dn = dropoff_name.strip().lower()
    start = ride.start_location.strip().lower()
    end = ride.end_location.strip().lower()

    route = (
        [start]
        + [s.strip().lower() for s in ride.stops.values_list('name', flat=True)]
        + [end]
    )

    if pn == dn:
        return False
    if pn == end:
        return False
    if dn == start:
        return False
    if pn == start and dn in route:
        return True
    if dn == end and pn in route:
        return True
    intermediate = route[1:-1]
    if pn in intermediate and dn in intermediate:
        return True
    return False


def find_best_carpool(pickup_name: str, dropoff_name: str, date_str: str, time_str: str):
    from datetime import timedelta
    naive_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    dt = timezone.make_aware(naive_dt)

    # Search rides departing from the requested time up to 3 hours later
    rides = Ride.objects.filter(
        departure_time__gte=dt,
        departure_time__lt=dt + timedelta(hours=3),
        available_seats__gte=1,
        status__in=['pending', 'confirmed'],
    )

    matches = [r for r in rides if can_serve(r, pickup_name, dropoff_name)]
    matches.sort(key=lambda r: (r.departure_time, r.seat_price, r.id))

    if not matches:
        return None

    ride = matches[0]
    driver_name = ride.driver.get_full_name() or ride.driver.username
    return {
        'id': ride.id,
        'driver_name': driver_name,
        'start_location': ride.start_location,
        'end_location': ride.end_location,
        'departure_time': ride.departure_time.isoformat(),
        'seat_price': str(ride.seat_price),
        'available_seats': ride.available_seats,
    }


def find_buses(pickup_name: str, dropoff_name: str, time_str: str = None) -> list:
    from datetime import time as time_type, timedelta, datetime, date as date_type

    pickup_filter = BusSchedule.objects.filter(
        stop__name__icontains=pickup_name
    ).values_list('bus_id', flat=True)

    dropoff_filter = BusSchedule.objects.filter(
        stop__name__icontains=dropoff_name
    ).values_list('bus_id', flat=True)

    bus_ids = set(pickup_filter) & set(dropoff_filter)

    min_time = None
    if time_str:
        try:
            h, m = time_str.split(':')
            min_time = time_type(int(h), int(m))
        except (ValueError, AttributeError):
            pass

    results = []
    for bus in Bus.objects.filter(id__in=bus_ids):
        unique_stop_count = BusSchedule.objects.filter(bus=bus).values('stop').distinct().count()

        # Derive the max valid journey time from the actual schedule spacing.
        # Sort all distinct arrival times and find the largest consecutive gap —
        # that represents the per-stop interval. Max journey = (stops-1) × that gap.
        distinct_times = sorted(
            BusSchedule.objects.filter(bus=bus)
            .values_list('arrival_time', flat=True)
            .distinct()
        )
        if len(distinct_times) >= 2:
            max_gap_minutes = max(
                (datetime.combine(date_type.today(), distinct_times[i + 1])
                 - datetime.combine(date_type.today(), distinct_times[i])).total_seconds() / 60
                for i in range(len(distinct_times) - 1)
            )
            max_journey = timedelta(minutes=max_gap_minutes * max(unique_stop_count - 1, 1))
        else:
            max_journey = timedelta(hours=2)

        pickup_schedules = BusSchedule.objects.filter(
            bus=bus, stop__name__icontains=pickup_name
        ).select_related('stop').order_by('arrival_time')

        dropoff_schedules = BusSchedule.objects.filter(
            bus=bus, stop__name__icontains=dropoff_name
        ).select_related('stop').order_by('arrival_time')

        base = datetime.combine(date_type.today(), time_type(0, 0))

        for ps in pickup_schedules:
            if min_time and ps.arrival_time < min_time:
                continue
            pt = datetime.combine(date_type.today(), ps.arrival_time)
            for ds in dropoff_schedules:
                dt = datetime.combine(date_type.today(), ds.arrival_time)
                gap = dt - pt
                if timedelta(0) < gap <= max_journey:
                    results.append({
                        'bus_name': bus.name,
                        'pickup_stop': ps.stop.name,
                        'dropoff_stop': ds.stop.name,
                        'pickup_time': ps.arrival_time.strftime('%H:%M'),
                        'dropoff_time': ds.arrival_time.strftime('%H:%M'),
                        'start_time': ps.arrival_time,
                        'bus': bus,
                        'start': pickup_name,
                    })
                    break

    results.sort(key=lambda x: x['start_time'])
    return results[:5]


def find_departures_at_stop(stop_name: str, time_str: str = None) -> list:
    """Return the next departures from any bus that stops at stop_name."""
    from datetime import time as time_type

    min_time = None
    if time_str:
        try:
            h, m = time_str.split(':')
            min_time = time_type(int(h), int(m))
        except (ValueError, AttributeError):
            pass

    schedules = (
        BusSchedule.objects
        .filter(stop__name__icontains=stop_name)
        .select_related('bus', 'stop')
        .order_by('arrival_time')
    )
    if min_time:
        schedules = schedules.filter(arrival_time__gte=min_time)

    seen = set()
    results = []
    for s in schedules:
        key = s.bus_id
        if key not in seen:
            seen.add(key)
            results.append({
                'bus_name': s.bus.name,
                'stop_name': s.stop.name,
                'departure_time': s.arrival_time.strftime('%H:%M'),
            })
        if len(results) >= 6:
            break
    return results


def create_booking(user, ride_id: int, pickup_name: str, seats: int = 1) -> dict:
    try:
        ride = Ride.objects.get(id=ride_id)
    except Ride.DoesNotExist:
        return {'success': False, 'error': 'Ride not found.'}

    if ride.available_seats < seats:
        if ride.available_seats == 0:
            return {'success': False, 'error': 'No seats available.'}
        return {'success': False, 'error': f'Only {ride.available_seats} seat(s) available on this ride.'}

    stop = find_stop(pickup_name)
    if stop is None:
        return {'success': False, 'error': 'Stop not found.'}

    booking = Booking.objects.create(
        passenger=user,
        ride=ride,
        stop=stop,
        seats=seats,
        status='pending',
    )
    ride.available_seats -= seats
    ride.save()

    driver_name = ride.driver.get_full_name() or ride.driver.username
    return {
        'success': True,
        'booking_id': booking.id,
        'from': ride.start_location,
        'to': ride.end_location,
        'departure': ride.departure_time.strftime('%Y-%m-%dT%H:%M'),
        'driver': driver_name,
        'price': str(ride.seat_price),
        'seats_booked': seats,
        'seats_left': ride.available_seats,
    }
