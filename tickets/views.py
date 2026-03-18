from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .services import acquire_seat_lock, get_session_seat_status, take_seat
from .serializers import SeatStatusSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Ticket
from .serializers import UserTicketSerializer


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
            return Response(
                {"error": "Você tem que ter a cadeira temporartiamente reservada antes de permanentemente reservar"},
                status=status.HTTP_409_CONFLICT
            )

        return Response({"message": "Cadeira reservada"}, status=status.HTTP_201_CREATED)
    
class UserTicketsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # todo: paginate
        user = request.user
        filter_type = request.query_params.get("filter", "all")

        queryset = Ticket.objects.filter(
            user=user,
        ).select_related(
            "session", "seat"
        )

        now = timezone.now()

        if filter_type == "future":
            queryset = queryset.filter(session__start_time__gt=now)

        elif filter_type == "past":
            queryset = queryset.filter(session__start_time__lt=now)

        queryset = queryset.order_by("session__start_time")

        paginator = PageNumberPagination()
        paginator.page_size = 1

        page = paginator.paginate_queryset(queryset, request)

        serializer = UserTicketSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)
        