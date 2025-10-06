from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.db.models import F
from django.contrib import messages
from .models import Room, Booking

def room_list(request):
    rooms = Room.objects.filter(is_open=True, available_hours__gt=0)
    return render(request, 'bookings/room_list.html', {'rooms': rooms})

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    has_booked = False
    if request.user.is_authenticated:
        has_booked = Booking.objects.filter(user=request.user, room=room).exists()
    return render(request, 'bookings/room_detail.html', {'room': room, 'has_booked': has_booked})

@login_required
def book_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if Booking.objects.filter(user=request.user, room=room).exists():
        messages.error(request, 'คุณได้จองห้องนี้แล้ว')
        return redirect('room_detail', pk=room.pk)
    with transaction.atomic():
        room = Room.objects.select_for_update().get(pk=room.pk)
        if not room.is_open or room.available_hours <= 0:
            messages.error(request, 'ไม่สามารถจองห้องนี้ได้ (ปิดหรือไม่มีชั่วโมงว่าง)')
            return redirect('room_detail', pk=room.pk)
        Booking.objects.create(user=request.user, room=room, hours=1)
        room.available_hours = F('available_hours') - 1
        room.save()
    messages.success(request, 'จองห้องเรียบร้อยแล้ว')
    return redirect('my_bookings')

@login_required
def my_bookings(request):
    bookings = request.user.bookings.select_related('room')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    with transaction.atomic():
        room = Room.objects.select_for_update().get(pk=booking.room.pk)
        booking.delete()
        room.available_hours = F('available_hours') + 1
        room.save()
    messages.success(request, 'ยกเลิกการจองเรียบร้อยแล้ว')
    return redirect('my_bookings')

@staff_member_required
def bookings_by_room(request):
    rooms = Room.objects.prefetch_related('bookings__user')
    return render(request, 'bookings/bookings_by_room.html', {'rooms': rooms})