from django.contrib import admin
from .models import Ride, Booking, Stop, Bus, BusSchedule, Review


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ['driver', 'start_location', 'end_location', 'departure_time', 'status', 'available_seats', 'seat_price']
    list_filter = ['status', 'departure_time', 'created_at']
    search_fields = ['start_location', 'end_location', 'driver__username']
    date_hierarchy = 'departure_time'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['passenger', 'ride', 'stop', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['passenger__username', 'ride__start_location', 'ride__end_location']
    date_hierarchy = 'created_at'


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(BusSchedule)
class BusScheduleAdmin(admin.ModelAdmin):
    list_display = ['bus', 'stop', 'arrival_time']
    list_filter = ['bus', 'stop']
    search_fields = ['bus__name', 'stop__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['passenger', 'driver', 'ride', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['passenger__username', 'driver__username', 'ride__start_location']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
