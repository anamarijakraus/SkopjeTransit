from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from rides.models import Booking, Ride
from .models import Profile


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('core:home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def switch_role(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if profile.role == 'driver':
        profile.role = 'passenger'
    else:
        profile.role = 'driver'

    profile.save()
    request.user.switch_role()
    return redirect('core:home_view')



@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if profile.role == 'driver':
        rides = Ride.objects.filter(driver=request.user)
        total_earnings = sum([
            ride.seat_price * Booking.objects.filter(ride=ride).count()
            for ride in rides
        ])
        context = {
            'user_type': 'driver',
            'rides': rides,
            'total_earnings': total_earnings,
        }
    else:
        bookings = Booking.objects.filter(passenger=request.user).select_related('ride')
        context = {
            'user_type': 'passenger',
            'bookings': bookings,
        }

    return render(request, 'profile.html', context)
