
from django.db import models
from django.conf import settings

class Ride(models.Model):
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='driven_rides')
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    stops = models.TextField()  # Comma-separated stop names
    seat_price = models.DecimalField(max_digits=6, decimal_places=2)
    available_seats = models.PositiveIntegerField()
    departure_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.origin} to {self.destination} by {self.driver.username}"

class Booking(models.Model):
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    stop = models.CharField(max_length=100)  # Where the passenger will get on
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passenger.username} booked {self.ride}"
