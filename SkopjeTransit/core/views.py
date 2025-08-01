from django.shortcuts import render
from rides.models import Ride, Stop, Bus, BusSchedule
from datetime import datetime
from django.utils import timezone


def home_view(request):
    stops = Stop.objects.all()

    if request.method == 'POST':
        start = request.POST.get('start_location')
        end = request.POST.get('end_location')
        time_str = request.POST.get('departure_time')
        time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M")

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
        # --- JSP Bus Matching ---
        buses_with_matching_route = []

        requested_time = time.time()

        for bus in Bus.objects.all():
            schedules = BusSchedule.objects.filter(bus=bus).order_by('arrival_time')

            for schedule in schedules:
                if schedule.stop.name == start and schedule.arrival_time >= requested_time:
                    buses_with_matching_route.append({
                        'bus': bus,
                        'start_time': schedule.arrival_time,
                        'start': start,
                    })
                    break

        # Sort buses by soonest start_time
        buses_with_matching_route = sorted(buses_with_matching_route, key=lambda b: b['start_time'])

        return render(request, 'ride_results.html', {
            'rides': matching_rides,
            'buses': buses_with_matching_route,
            'start': start,
            'end': end,
            'departure_time': time_str,
            'seats_requested': seats_requested,
            'stop_coordinates_json': json.dumps(STOP_COORDINATES),
            'bus_stops_json': json.dumps(BUS_STOPS),
        })

    return render(request, 'home.html', {'stops': stops})

import json

STOP_COORDINATES = {
"Gjorce Petrov Polyclinic": (42.009960610861896, 21.362986632943255),
    "Gjorce Petrov Cinema": (42.00662951598224, 21.359833180961385),
    "Gjorce Petrov Old Market": (42.006750953076114, 21.36402442218535),
    "Vlae Porta": (42.00825683035508, 21.369316130783005),
    "Vlae": (42.00711329977916, 21.37406878408426),
    "Dolno Nerezi": (42.00457410343205, 21.384265565139565),
    "Skopje City Archives": (42.003510684138014, 21.391331740119895),
    "Karposh 3 Gas Station": (42.00310071847542, 21.39423590705844),
    "Bucharest Polyclinic": (42.002339451681536, 21.399977657069385),
    "Taftalidze T": (42.00152935857006, 21.384565404640817),
    "Taftalidze Market": (42.00100550117513, 21.389712077594297),
    "Karposh 4 TC City Mall T": (42.0053290296922, 21.39072284092892),
    "Restaurant Imes": (42.00751418026308, 21.394789405143506),
    "Primary School Lazo Trpovski": (42.00730366344567, 21.39920419939792),
    "Hospital 8mi Septemvri": (42.00402606408907, 21.40168589592222),
    "Karposh 2": (42.00154804118411, 21.405869204032985),
    "Mal Odmor": (42.00077466663705, 21.412140208620638),
    "Bunjakovec Shopping Center": (41.99937651802242, 21.418762314523686),
    "Bunjakovec Porta": (41.99830415123952, 21.423990722179596),
    "Centar Record": (41.99422984697384, 21.43174611989921),
    "Zelen Pazar": (41.99194041975922, 21.43405661299886),
    "Kuzman Josifoski Pitu Primary School": (41.98688523246464, 21.43283482363934),
    "Championche": (41.98200372183693, 21.435083280079887),
    "Kisela Voda Przino": (41.97722385066787, 21.43760595712438),
    "Home For The Blind": (41.97636705301183, 21.443168473278284),
    "Krume Kepeski Primary School": (41.97194829044498, 21.444893204087958),
    "Bilna Apteka": (41.98948397993322, 21.435775776702606),
    "Cheshma Kisela Voda Maxi": (41.98326995129605, 21.43932800747017),
    "Jugodrvo Olympic Pool": (41.99225214793168, 21.438732111762686),
    "Vero Jambo": (41.993316191387684, 21.44240725668731),
    "Railway Station": (41.99083808820962, 21.446556271783642),
    "Intercity Bus": (41.9911512963059, 21.44461307900404),
    "Tobacco Factory": (41.986837791084405, 21.443886809357064),
    "Dimitar Vlahov Secondary School": (41.982286098502684, 21.45343562642649),
    "Rade Koncar Petrol Station": (41.98249294364782, 21.45286015954903),
    "Transporten Center T": (41.990268436340685, 21.445074876415976),
    "TC Skopjanka": (41.98878486950928, 21.44993246819053),
    "Aerodrom Tobacco 2": (41.98790532105144, 21.453107008880874),
    "TC Tri Biseri": (41.98899811279343, 21.457663043383025),
    "Posta Telecom": (41.99781480869749, 21.428646822542206),
    "Most Goce Delchev Theater": (41.99914584635948, 21.432839785751856),
    "National University Library": (41.998168433004906, 21.44033143710131),
    "Bitpazar 1 University of St. Cyril and Methodius": (42.00035031321308, 21.44027497617046),
    "Yaja Pasha Mosque": (42.00748682650819, 21.44292325659743),
    "Chair": (42.011424942193436, 21.444811531787433),
    "Chair Buildings": (42.01843163424498, 21.447837063598914),
    "Chair Polyclinic": (42.02148678542643, 21.448508420271573),
    "Church of St. Nicholas": (42.02187974591609, 21.43904574588007),
    "Bitpazar 2 Shopping Center": (42.00131639001992, 21.44017542976259),
    "Primary School Bitola Congress": (42.0027826502703, 21.4436047823371),
    "Hotel Continental": (41.99937275572648, 21.45300647039361)
}
BUS_STOPS = {
    '2': ["Gjorce Petrov Cinema", "Gjorce Petrov Old Market", "Vlae Porta", "Vlae", "Dolno Nerezi",
          "Skopje City Archives",
          "Karposh 3 Gas Station", "Bucharest Polyclinic", "Karposh 2", "Mal Odmor", "Bunjakovec Shopping Center",
          "Posta Telecom", "Most Goce Delchev Theater", "Bitpazar 2 Shopping Center", "Primary School Bitola Congress"
        ,"Hotel Continental"
],

'4': [
    "Gjorce Petrov Cinema", "Gjorce Petrov Old Market", "Vlae Porta", "Vlae", "Dolno Nerezi", "Skopje City Archives",
    "Karposh 3 Gas Station", "Bucharest Polyclinic", "Karposh 2", "Mal Odmor", "Bunjakovec Shopping Center",
    "Bunjakovec Porta", "Centar Record", "Zelen Pazar", "Bilna Apteka", "Cheshma Kisela Voda Maxi"
],

'7': [
    "Karposh 3 TC City Mall T", "Restaurant Imes", "Primary School Lazo Trpovski", "Hospital 8mi Septemvri",
    "Karposh 2", "Mal Odmor",
    "Bunjakovec Shopping Center", "Bunjakovec Porta", "Centar Record", "Zelen Pazar", "Jugodrvo Olympic Pool",
    "Vero Jambo", "Intercity Bus",
    "Tobacco Factory", " Dimitar Vlahov Secondary School", "Rade Koncar Petrol Station"
],

'15': [
    "Karposh 4 TC City Mall T", "Restaurant Imes", "Primary School Lazo Trpovski", "Hospital 8mi Septemvri",
    "Karposh 2", "Mal Odmor",
    "Bunjakovec Shopping Center", "Bunjakovec Porta", "Centar Record", "Zelen Pazar", "Jugodrvo Olympic Pool",
    "Vero Jambo",
    "Railway Station", "TC Skopjanka", "Aerodrom Tobacco 2", "TC Tri Biseri"
],

'19': [
    "Karposh 4 TC City Mall T", "Restaurant Imes", "Primary School Lazo Trpovski", "Hospital 8mi Septemvri",
    "Karposh 2", "Mal Odmor",
    "Bunjakovec Shopping Center", "Bunjakovec Porta", "Posta Telecom", " Most Goce Delchev Theater",
    "Bitpazar 1 University of St. Cyril and Methodius",
    "Yaja Pasha Mosque", "Chair", "Chair Buildings", "Chair Polyclinic", "Church of St. Nicholas"
],

'22': [
    "Gjorce Petrov Polyclinic", "Vlae Porta", "Vlae", "Dolno Nerezi", "Skopje City Archives", "Karposh 3 Gas Station",
    "Bucharest Polyclinic", "Karposh 2", "Mal Odmor",
    "Bunjakovec Shopping Center", "Bunjakovec Porta", "Centar Record", "Zelen Pazar", "Jugodrvo Olympic Pool",
    "Vero Jambo", "Intercity Bus"
],

'24': [
    "Taftalidze T", "Taftalidze Market", "Skopje City Archives", "Karposh 3 Gas Station", "Bucharest Polyclinic",
    "Karposh 2", "Mal Odmor",
    "Bunjakovec Shopping Center", "Bunjakovec Porta", "Centar Record", "Zelen Pazar",
    "Kuzman Josifoski Pitu Primary School", "Championche",
    "Kisela Voda Przino", "Home For The Blind", "Krume Kepeski Primary School"
],

'60': [
    "Gjorce Petrov Cinema", "Gjorce Petrov Old Market", "Vlae Porta", "Vlae", "Dolno Nerezi", "Skopje City Archives",
"Karposh 3 Gas Station", "Bucharest Polyclinic", "Karposh 2", "Mal Odmor", "Bunjakovec Shopping Center",
"Posta Telecom", " Most Goce Delchev Theater", "National University Library", "Vero Jambo", "Transporten Center T",
]

}

def bus_map(request):
    return render(request, 'ride_results.html', {
        'rides': rides,
        'buses': buses,
        'stop_coordinates_json': json.dumps(STOP_COORDINATES),
        'bus_stops_json': json.dumps(BUS_STOPS),
    })