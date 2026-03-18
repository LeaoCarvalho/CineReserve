from rest_framework import serializers


class SeatStatusSerializer(serializers.Serializer):
    seat_id = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=["available", "locked", "taken"]
    )
