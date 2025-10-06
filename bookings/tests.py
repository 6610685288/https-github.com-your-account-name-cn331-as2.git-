# bookings/tests/test_core.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from bookings.models import Room, Booking

User = get_user_model()

class BookingAppTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='pass1234')
        self.user2 = User.objects.create_user(username='user2', password='pass4321')

        self.room_open = Room.objects.create(
            code='R101', name='Room 101', capacity=30,
            total_hours=5, available_hours=2, is_open=True
        )
        self.room_closed = Room.objects.create(
            code='R102', name='Room 102', capacity=20,
            total_hours=3, available_hours=0, is_open=False
        )

    def test_login_success_and_failure(self):
        login_url = reverse('login') 
        r = self.client.get(login_url)
        self.assertEqual(r.status_code, 200)

        r = self.client.post(login_url, {'username': 'user1', 'password': 'wrongpass'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'password', status_code=200)  

        r = self.client.post(login_url, {'username': 'user1', 'password': 'pass1234'}, follow=True)
        self.assertEqual(r.status_code, 200)
        user = r.context['user']
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, 'user1')

    def test_room_booking_success(self):
        self.client.login(username='user1', password='pass1234')

        book_url = reverse('book_room', args=[self.room_open.pk])
        response = self.client.post(book_url, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(Booking.objects.filter(user=self.user, room=self.room_open).exists())

        self.room_open.refresh_from_db()
        self.assertEqual(self.room_open.available_hours, 1)

    def test_room_booking_already_booked_by_same_user(self):
        Booking.objects.create(user=self.user, room=self.room_open, hours=1)
        self.room_open.available_hours -= 1
        self.room_open.save()

        self.client.login(username='user1', password='pass1234')
        book_url = reverse('book_room', args=[self.room_open.pk])
        response = self.client.post(book_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.filter(user=self.user, room=self.room_open).count(), 1)

    def test_room_booking_when_no_available_hours(self):
        self.client.login(username='user2', password='pass4321')
        book_url = reverse('book_room', args=[self.room_closed.pk])
        response = self.client.post(book_url, follow=True)
        self.assertFalse(Booking.objects.filter(user=self.user2, room=self.room_closed).exists())
        self.assertEqual(response.status_code, 200)

    def test_cancel_booking(self):
        b = Booking.objects.create(user=self.user, room=self.room_open, hours=1)
        self.room_open.available_hours -= 1
        self.room_open.save()

        self.client.login(username='user1', password='pass1234')
        cancel_url = reverse('cancel_booking', args=[b.pk])
        response = self.client.post(cancel_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Booking.objects.filter(pk=b.pk).exists())
        self.room_open.refresh_from_db()
        self.assertEqual(self.room_open.available_hours, 2) 
