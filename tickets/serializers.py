from rest_framework import serializers
from .models import Ticket

class SeatStatusSerializer(serializers.Serializer):
    seat_id = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=["available", "locked", "taken"]
    )

class UserTicketSerializer(serializers.ModelSerializer):
    session_start = serializers.DateTimeField(source="session.start_time")
    movie_title = serializers.CharField(source="session.movie.title")
    label = serializers.CharField(source="seat.label")

    class Meta:
        model = Ticket
        fields = ["id", "movie_title", "session_start", "label"]