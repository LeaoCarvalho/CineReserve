from django.db import models
from django.utils import timezone
from datetime import timedelta
from users.models import CustomUser
from sessions.models import Session
from seats.models import Seat


class Ticket(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session", "seat"],
                name="unique_seat_per_session"
            )
        ]
