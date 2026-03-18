from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .services import acquire_seat_lock, get_session_seat_status, take_seat
from .serializers import SeatStatusSerializer


class LockSeatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id, seat_id):
        user_id = request.user.id

        success = acquire_seat_lock(session_id, seat_id, user_id)

        if not success:
            return Response(
                {"error": "Cadeira já reservada!"},
                status=status.HTTP_409_CONFLICT
            )

        return Response({"message": "Cadeira temporariamente reservada"}, status=status.HTTP_201_CREATED)

class SessionSeatsView(APIView):
    # todo: precisa autenticar?

    def get(self, request, session_id):
        seat_data = get_session_seat_status(session_id)
        serializer = SeatStatusSerializer(seat_data, many=True)
        return Response(serializer.data)

class TakeSeatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id, seat_id):
        user_id = request.user.id

        success = take_seat(session_id, seat_id, user_id)

        if not success:
            # todo: melhorar a resposta
            return Response(
                {"error": "Você tem que ter a cadeira temporartiamente reservada antes de permanentemente reservar"},
                status=status.HTTP_409_CONFLICT
            )

        return Response({"message": "Cadeira reservada"}, status=status.HTTP_201_CREATED)