from django.db import models
from django.conf import settings


class Ride(models.Model):
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='driven_rides')
    start_location = models.CharField(max_length=100)
    end_location = models.CharField(max_length=100)
    stops = models.ManyToManyField('Stop')
    seat_price = models.DecimalField(max_digits=6, decimal_places=2)
    available_seats = models.PositiveIntegerField()
    departure_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.start_location} to {self.end_location} by {self.driver.username}"


class Booking(models.Model):
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    stop = models.ForeignKey('Stop', on_delete=models.CASCADE)  # Where the passenger will get on
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passenger.username} booked {self.ride}"


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
