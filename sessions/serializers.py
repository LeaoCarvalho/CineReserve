from rest_framework import serializers
from .models import Session

class SessionSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "room_name",
            "start_time",
            "screening_format",
            "language_version",
            "price",
            "status",
        ]