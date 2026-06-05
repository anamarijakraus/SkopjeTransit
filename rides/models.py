from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Ride(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='driven_rides')
    start_location = models.CharField(max_length=100)
    end_location = models.CharField(max_length=100)
    stops = models.ManyToManyField('Stop')
    seat_price = models.DecimalField(max_digits=6, decimal_places=2)
    available_seats = models.PositiveIntegerField()
    departure_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    start_time = models.DateTimeField(null=True, blank=True)  # When ride actually started
    end_time = models.DateTimeField(null=True, blank=True)    # When ride actually ended

    def __str__(self):
        return f"{self.start_location} to {self.end_location} by {self.driver.username}"

    @property
    def is_past_departure(self):
        from django.utils import timezone
        return self.departure_time < timezone.now()

    @property
    def is_ongoing(self):
        return self.status == 'ongoing' and self.start_time and not self.end_time


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    stop = models.ForeignKey('Stop', on_delete=models.CASCADE)  # Where the passenger will get on
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.passenger.username} booked {self.ride}"


class Review(models.Model):
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passenger.username} rated {self.driver.username} {self.rating} stars"

    class Meta:
        ordering = ['-created_at']


class Stop(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Bus(models.Model):
    name = models.CharField(max_length=20)  # e.g. "Bus 22"

    def __str__(self):
        return self.name


class BusSchedule(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='schedules')
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    arrival_time = models.TimeField()  # only time (not date)

    class Meta:
        ordering = ['arrival_time']  # ensures stops are in order

    def __str__(self):
        return f"{self.bus.name} - {self.stop.name} at {self.arrival_time}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('ride_payment', 'Ride Payment'),
        ('refund', 'Refund'),
        ('top_up', 'Top Up'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions_made')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions_received')
    amount = models.IntegerField()  # Total amount paid (MKD - no decimals)
    driver_amount = models.IntegerField()  # Amount driver receives (90%)
    platform_fee = models.IntegerField()  # Platform fee (10%)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='ride_payment')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passenger.username} → {self.driver.username}: {self.amount} MKD"

    class Meta:
        ordering = ['-created_at']
