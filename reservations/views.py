from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Classroom, Booking

def classroom_list(request):
    classrooms = Classroom.objects.filter(is_active=True)
    return render(request, 'reservations/classroom_list.html', {'classrooms': classrooms})

@login_required
def book_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    if classroom.available_hours > 0:
        booking, created = Booking.objects.get_or_create(user=request.user, classroom=classroom, defaults={'booked_hour': 1})
        if created:
            classroom.available_hours -= 1
            classroom.save()
    return redirect('my_bookings')

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'reservations/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    classroom = booking.classroom
    classroom.available_hours += 1
    classroom.save()
    booking.delete()
    return redirect('my_bookings')

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def booking_list(request):
    bookings = Booking.objects.select_related('user', 'classroom')
    return render(request, 'reservations/booking_list.html', {'bookings': bookings})
