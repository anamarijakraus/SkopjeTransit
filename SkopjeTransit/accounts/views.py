from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from rides.models import Booking, Ride, Review
from .models import Profile


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:home_view')
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
            return redirect('core:home_view')
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
        profile.save()
        request.user.switch_role()
    else:
        profile.role = 'driver'
        profile.save()
        request.user.switch_role()
    return redirect('core:home_view')


@login_required
def join_community(request):
    """
    Handle the "Join the community" button functionality:
    1. If user is passenger, switch to driver and redirect to create ride
    2. If user is driver, just redirect to create ride
    """
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if profile.role == 'passenger':
        # Switch to driver role
        profile.role = 'driver'
        profile.save()
        request.user.switch_role()
        return redirect('rides:create')
    else:
        # Already a driver, just redirect to create ride
        return redirect('rides:create')


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    now = timezone.now()

    if profile.role == 'driver':
        # Current rides (not past departure)
        current_rides = Ride.objects.filter(
            driver=request.user,
            departure_time__gte=now,
            status__in=['confirmed', 'ongoing']
        ).order_by('departure_time')
        
        # Pending ride requests
        pending_bookings = Booking.objects.filter(
            ride__driver=request.user,
            status='pending'
        ).select_related('passenger', 'ride').order_by('-created_at')
        
        # Reviews received
        reviews = Review.objects.filter(driver=request.user).order_by('-created_at')
        
        # Calculate total earnings from completed rides
        completed_bookings = Booking.objects.filter(
            ride__driver=request.user,
            status='completed'
        )
        total_earnings = sum([
            booking.ride.seat_price for booking in completed_bookings
        ])
        
        context = {
            'user_type': 'driver',
            'current_rides': current_rides,
            'pending_bookings': pending_bookings,
            'reviews': reviews,
            'total_earnings': total_earnings,
        }
    else:
        # Confirmed bookings (not past departure) - for Booked Rides tab
        confirmed_bookings = Booking.objects.filter(
            passenger=request.user,
            ride__departure_time__gte=now,
            status='confirmed'
        ).select_related('ride').order_by('ride__departure_time')
        
        # Pending bookings
        pending_bookings = Booking.objects.filter(
            passenger=request.user,
            status='pending'
        ).select_related('ride').order_by('-created_at')
        
        # Ongoing bookings
        ongoing_bookings = Booking.objects.filter(
            passenger=request.user,
            status='ongoing'
        ).select_related('ride').order_by('-started_at')
        
        context = {
            'user_type': 'passenger',
            'confirmed_bookings': confirmed_bookings,
            'pending_bookings': pending_bookings,
            'ongoing_bookings': ongoing_bookings,
        }

    return render(request, 'profile.html', context)


@login_required
def ride_history_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    now = timezone.now()

    if profile.role == 'driver':
        # Past rides
        past_rides = Ride.objects.filter(
            driver=request.user,
            departure_time__lt=now
        ).order_by('-departure_time')
        
        context = {
            'user_type': 'driver',
            'rides': past_rides,
        }
    else:
        # Past bookings
        past_bookings = Booking.objects.filter(
            passenger=request.user,
            ride__departure_time__lt=now
        ).select_related('ride').order_by('-ride__departure_time')
        
        context = {
            'user_type': 'passenger',
            'bookings': past_bookings,
        }

    return render(request, 'ride_history.html', context)


@login_required
@require_POST
def confirm_ride(request, booking_id):
    """Driver confirms a passenger's ride request"""
    if request.user.profile.role != 'driver':
        return JsonResponse({'error': 'Only drivers can confirm rides'}, status=403)
    
    booking = get_object_or_404(Booking, id=booking_id, ride__driver=request.user)
    booking.status = 'confirmed'
    booking.confirmed_at = timezone.now()
    booking.save()
    
    messages.success(request, f'Ride confirmed for {booking.passenger.username}')
    return JsonResponse({'success': True})


@login_required
@require_POST
def start_ride(request, booking_id):
    """Passenger starts a ride"""
    if request.user.profile.role != 'passenger':
        return JsonResponse({'error': 'Only passengers can start rides'}, status=403)
    
    booking = get_object_or_404(Booking, id=booking_id, passenger=request.user)
    if booking.status != 'confirmed':
        return JsonResponse({'error': 'Ride must be confirmed before starting'}, status=400)
    
    booking.status = 'ongoing'
    booking.started_at = timezone.now()
    booking.save()
    
    # Update ride status
    ride = booking.ride
    ride.status = 'ongoing'
    ride.start_time = timezone.now()
    ride.save()
    
    messages.success(request, 'Ride started!')
    return JsonResponse({'success': True})


@login_required
@require_POST
def end_ride(request, booking_id):
    """Passenger ends a ride"""
    if request.user.profile.role != 'passenger':
        return JsonResponse({'error': 'Only passengers can end rides'}, status=403)
    
    try:
        booking = get_object_or_404(Booking, id=booking_id, passenger=request.user)
        if booking.status != 'ongoing':
            return JsonResponse({'error': 'Ride must be ongoing before ending'}, status=400)
        
        # Update booking status
        booking.status = 'completed'
        booking.completed_at = timezone.now()
        booking.save()
        
        # Update ride status
        ride = booking.ride
        ride.status = 'completed'
        ride.end_time = timezone.now()
        ride.save()
        
        messages.success(request, 'Ride completed!')
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': f'Error ending ride: {str(e)}'}, status=500)


@login_required
@require_POST
def submit_review(request, booking_id):
    """Passenger submits a review for a completed ride"""
    if request.user.profile.role != 'passenger':
        return JsonResponse({'error': 'Only passengers can submit reviews'}, status=403)
    
    try:
        data = json.loads(request.body)
        rating = data.get('rating')
        comment = data.get('comment')
        
        if not rating or not comment:
            return JsonResponse({'error': 'Rating and comment are required'}, status=400)
        
        if not (1 <= int(rating) <= 5):
            return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
        
        # First try to find the booking by ID and passenger
        try:
            booking = Booking.objects.get(id=booking_id, passenger=request.user)
        except Booking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        
        # Check if the ride is completed
        if booking.status != 'completed':
            return JsonResponse({'error': 'Can only review completed rides'}, status=400)
        
        # Create or update review
        review, created = Review.objects.get_or_create(
            passenger=request.user,
            driver=booking.ride.driver,
            ride=booking.ride,
            defaults={'rating': rating, 'comment': comment}
        )
        
        if not created:
            review.rating = rating
            review.comment = comment
            review.save()
        
        messages.success(request, 'Review submitted successfully!')
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error submitting review: {str(e)}'}, status=500)
