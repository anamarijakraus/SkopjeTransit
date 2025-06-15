from django.shortcuts import render
from rides.models import Ride, Stop
from django.utils import timezone
from django.db.models import Q

def home_view(request):
    stops = Stop.objects.all()

    if request.method == 'POST':
        start = request.POST.get('start_location')
        end = request.POST.get('end_location')
        time = request.POST.get('departure_time')

        try:
            seats_requested = int(request.POST.get('seats', '1'))
            if seats_requested < 1:
                seats_requested = 1
        except ValueError:
            seats_requested = 1

        # Initial filter: only future rides with enough seats
        rides = Ride.objects.filter(
            departure_time__gte=time,
            available_seats__gte=seats_requested
        )

        matching_rides = []
        for ride in rides:
            # Build the route: start + stops + end
            route_stops = list(ride.stops.values_list('name', flat=True))
            full_route = [ride.start_location] + route_stops + [ride.end_location]

            # Passenger start is valid if it's in start or stops, but not end
            is_start_valid = (
                start == ride.start_location or start in route_stops
            ) and start != ride.end_location

            if is_start_valid:
                matching_rides.append(ride)

        return render(request, 'ride_results.html', {
            'rides': matching_rides,
            'start': start,
            'end': end,
            'departure_time': time,
            'seats_requested': seats_requested,
        })

    return render(request, 'home.html', {'stops': stops})