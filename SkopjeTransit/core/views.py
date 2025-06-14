from django.shortcuts import render
from rides.models import Ride

# def home(request):
#     return render(request, 'home.html')
#

def home_view(request):
    rides = Ride.objects.filter(available_seats__gt=0).order_by('departure_time')
    return render(request, 'home.html', {'rides': rides})