from django.contrib import admin
from .models import Room, Booking


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'capacity', 'total_hours', 'available_hours', 'is_open')
    list_editable = ('is_open',)
    search_fields = ('code', 'name')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'created_at', 'hours')
    list_filter = ('room', 'created_at')
    search_fields = ('user__username', 'room__code')