from django.db import models
from django.conf import settings


class Room(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField(default=1)

    total_hours = models.PositiveIntegerField(default=0)

    available_hours = models.PositiveIntegerField(default=0)

    is_open = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.code} - {self.name}"

class Booking(models.Model):
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    hours = models.PositiveSmallIntegerField(default=1)


    class Meta:
        unique_together = (('user', 'room'),)


    def __str__(self):
        return f"{self.user} -> {self.room} @ {self.created_at:%Y-%m-%d %H:%M}"