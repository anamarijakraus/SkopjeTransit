from django import forms
from .models import Ride
from .models import Booking


class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['start_location', 'end_location', 'stops', 'departure_time', 'seat_price', 'available_seats']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'stops': forms.CheckboxSelectMultiple(),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['stop']
        labels = {
            'stop': 'Pick up Spot'
        }
        widgets = {
            'stop': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        ride = kwargs.pop('ride', None)
        super().__init__(*args, **kwargs)
        if ride:
            self.fields['stop'].queryset = ride.stops.all()
