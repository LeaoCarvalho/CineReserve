from django.db import models
from rooms.models import Room

class Seat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    label = models.CharField(max_length=10)

    class Meta:
        unique_together = ("room", "label")
