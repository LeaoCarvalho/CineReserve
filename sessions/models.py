from django.db import models
from movies.models import Movie
from rooms.models import Room

class Session(models.Model):

    class ScreeningFormat(models.TextChoices):
        TWO_D = "2D", "2D"
        THREE_D = "3D", "3D"
        IMAX = "IMAX", "IMAX"
        FOUR_DX = "4DX", "4DX"

    class LanguageVersion(models.TextChoices):
        DUBBED = "DUBBED", "Dubbed"
        SUBTITLED = "SUBTITLED", "Subtitled"
        ORIGINAL = "ORIGINAL", "Original"

    class SessionStatus(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        CANCELLED = "CANCELLED", "Cancelled"
        SOLD_OUT = "SOLD_OUT", "Sold Out"
        FINISHED = "FINISHED", "Finished"

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    screening_format = models.CharField(
        max_length=10,
        choices=ScreeningFormat.choices
    )
    language_version = models.CharField(
        max_length=20,
        choices=LanguageVersion.choices
    )
    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.SCHEDULED
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["room", "start_time"],
                name="unique_session_per_room_time"
            )
        ]