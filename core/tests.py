from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import time, timedelta
from rides.models import Ride, Stop, Bus, BusSchedule
from core.services import transit

User = get_user_model()


class CanServeTest(TestCase):
    def setUp(self):
        self.driver = User.objects.create_user(username='driver1', password='testpass')
        self.ride = Ride.objects.create(
            driver=self.driver,
            start_location='Aerodrom Tobacco 2',
            end_location='Karposh 2',
            seat_price=80,
            available_seats=3,
            departure_time=timezone.now() + timedelta(hours=2),
            status='confirmed',
        )

    def test_start_to_end_is_valid(self):
        self.assertTrue(transit.can_serve(self.ride, 'Aerodrom Tobacco 2', 'Karposh 2'))

    def test_reversed_is_invalid(self):
        self.assertFalse(transit.can_serve(self.ride, 'Karposh 2', 'Aerodrom Tobacco 2'))

    def test_same_pickup_and_dropoff_is_invalid(self):
        self.assertFalse(transit.can_serve(self.ride, 'Karposh 2', 'Karposh 2'))

    def test_unknown_stop_returns_false(self):
        self.assertFalse(transit.can_serve(self.ride, 'Nonexistent Stop', 'Karposh 2'))

    def test_dropoff_at_start_is_invalid(self):
        self.assertFalse(transit.can_serve(self.ride, 'Karposh 2', 'Aerodrom Tobacco 2'))


class FindBusesTest(TestCase):
    def setUp(self):
        self.bus = Bus.objects.create(name='Bus 15')
        self.stop_a = Stop.objects.create(name='Karposh 2')
        self.stop_b = Stop.objects.create(name='Railway Station')
        BusSchedule.objects.create(bus=self.bus, stop=self.stop_a, arrival_time=time(9, 0))
        BusSchedule.objects.create(bus=self.bus, stop=self.stop_b, arrival_time=time(9, 30))

    def test_finds_bus_for_valid_route(self):
        results = transit.find_buses('Karposh 2', 'Railway Station')
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['bus_name'], 'Bus 15')

    def test_does_not_find_bus_for_reversed_route(self):
        """Core bug fix verification: A->B bus must NOT appear for B->A query."""
        results = transit.find_buses('Railway Station', 'Karposh 2')
        self.assertEqual(len(results), 0)

    def test_time_filter_excludes_past_buses(self):
        results = transit.find_buses('Karposh 2', 'Railway Station', '10:00')
        self.assertEqual(len(results), 0)

    def test_time_filter_includes_matching_buses(self):
        results = transit.find_buses('Karposh 2', 'Railway Station', '08:00')
        self.assertGreater(len(results), 0)

    def test_bus_with_only_one_stop_not_returned(self):
        """Bus must serve BOTH stops, not just one."""
        Stop.objects.create(name='Isolated Stop')
        results = transit.find_buses('Karposh 2', 'Isolated Stop')
        self.assertEqual(len(results), 0)


class AssistantViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testpassenger', password='testpass')
        self.client = Client()

    def test_assistant_redirects_when_not_logged_in(self):
        response = self.client.get('/assistant/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/', response['Location'])

    def test_clear_chat_redirects(self):
        self.client.login(username='testpassenger', password='testpass')
        response = self.client.post('/assistant/clear/')
        self.assertEqual(response.status_code, 302)
