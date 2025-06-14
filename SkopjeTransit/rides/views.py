from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RideForm
from .models import Ride, Stop
from accounts.models import Profile
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Ride, Booking
from .forms import BookingForm

@login_required
def create_ride(request):
    profile = request.user.profile

    if profile.role != 'driver':
        return redirect('core:home')

    if request.method == 'POST':
        form = RideForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.driver = request.user
            ride.save()
            form.save_m2m()
            return redirect('accounts:profile')
    else:
        form = RideForm()

    return render(request, 'create_ride.html', {'form': form})


@login_required
def book_ride(request, ride_id):
    profile = request.user.profile
    if profile.role != 'passenger':
        return redirect('core:home')

    ride = get_object_or_404(Ride, id=ride_id)

    if request.method == 'POST':
        form = BookingForm(request.POST, ride=ride)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.ride = ride
            booking.passenger = request.user
            booking.save()
            ride.available_seats -= 1
            ride.save()
            return redirect('accounts:profile')
    else:
        form = BookingForm(ride=ride)

    return render(request, 'book_ride.html', {'form': form, 'ride': ride})