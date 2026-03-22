from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .services import acquire_seat_lock, get_session_seat_status, take_seat
from .serializers import SeatStatusSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Ticket
from .serializers import UserTicketSerializer
from django.http import HttpResponse


class LockSeatView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Lock a seat temporarily",
        operation_description=(
            "Attempts to lock a seat for the authenticated user. "
            "If the seat is already locked or reserved, a conflict error is returned."
        ),

        manual_parameters=[
            openapi.Parameter(
                'session_id',
                openapi.IN_PATH,
                description="ID of the session",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'seat_id',
                openapi.IN_PATH,
                description="ID of the seat",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],

        responses={
            201: openapi.Response(
                description="Seat successfully locked",
                examples={
                    "application/json": {
                        "message": "Cadeira temporariamente reservada"
                    }
                }
            ),
            409: openapi.Response(
                description="Seat already reserved or locked",
                examples={
                    "application/json": {
                        "error": "Cadeira já reservada!"
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required"
            ),
        },

        security=[{"Bearer": []}]  # if you're using JWT/Bearer auth
    )
    def post(self, request, session_id, seat_id):
        user_id = request.user.id

        lock_time_seconds_str = request.query_params.get("lock_time_seconds", "300")

        try:
            lock_time_seconds = int(lock_time_seconds_str)
            if lock_time_seconds <= 0 or lock_time_seconds > 600:
                raise ValueError
        except ValueError:
            return Response(
                {"detail": "Inválido, lock_time_seconds precisa ser de 1 a 600"},
                status=status.HTTP_400_BAD_REQUEST
            )

        success = acquire_seat_lock(session_id, seat_id, user_id, lock_time_seconds)

        if not success:
            return Response(
                {"error": "Cadeira já reservada!"},
                status=status.HTTP_409_CONFLICT
            )

        return Response({"message": "Cadeira temporariamente reservada"}, status=status.HTTP_201_CREATED)

class SessionSeatsView(APIView):

    @swagger_auto_schema(
        operation_summary="Get seat status for a session",
        operation_description=(
            "Returns the status of all seats for a given session. "
            "Includes availability, locked seats, and reserved seats."
        ),

        manual_parameters=[
            openapi.Parameter(
                'session_id',
                openapi.IN_PATH,
                description="ID of the session",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],

        responses={
            200: openapi.Response(
                description="List of seat statuses for the session",
                schema=SeatStatusSerializer(many=True)
            ),
            404: openapi.Response(
                description="Session not found"
            ),
        }
    )
    def get(self, request, session_id):
        seat_data = get_session_seat_status(session_id)
        serializer = SeatStatusSerializer(seat_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TakeSeatView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Confirm (take) a seat reservation",
        operation_description=(
            "Confirms a seat reservation for the authenticated user. "
            "The seat must be previously locked by the same user. "
            "If not, a conflict error is returned."
        ),

        manual_parameters=[
            openapi.Parameter(
                'session_id',
                openapi.IN_PATH,
                description="ID of the session",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'seat_id',
                openapi.IN_PATH,
                description="ID of the seat",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],

        responses={
            201: openapi.Response(
                description="Seat successfully reserved",
                examples={
                    "application/json": {
                        "message": "Cadeira reservada"
                    }
                }
            ),
            409: openapi.Response(
                description="Seat not locked by user or lock expired",
                examples={
                    "application/json": {
                        "error": "Você tem que ter a cadeira temporartiamente reservada antes de permanentemente reservar"
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required"
            ),
        },
    )
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


    @swagger_auto_schema(
        operation_summary="List user tickets",
        operation_description=(
            "Returns a paginated list of tickets for the authenticated user. "
            "You can filter tickets by time (past or future sessions)."
        ),

        manual_parameters=[
            openapi.Parameter(
                'filter',
                openapi.IN_QUERY,
                description="Filter tickets: 'all' (default), 'future', or 'past'",
                type=openapi.TYPE_STRING,
                enum=['all', 'future', 'past']
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER
            ),
        ],

        responses={
            200: openapi.Response(
                description="Paginated list of user tickets",
            ),
            401: openapi.Response(
                description="Authentication required"
            ),
        },
    )
    def get(self, request):
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
        
def session_seats_page(request, session_id):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Session {session_id} Seats</title>
    </head>
    <body>
        <h1>Session {session_id} Seats</h1>
        <ul id="seats"></ul>

        <script>
            const sessionId = {session_id};
            const seatsList = document.getElementById("seats");

            // Store current state
            const seatsState = {{}};

            function render() {{
                seatsList.innerHTML = "";
                Object.entries(seatsState).forEach(([seatId, status]) => {{
                    const li = document.createElement("li");
                    li.textContent = `Seat ${{seatId}}: ${{status}}`;
                    seatsList.appendChild(li);
                }});
            }}

            // 1. Fetch initial state (HTTP)
            fetch(`/tickets/session/${{sessionId}}/seats/`)
                .then(res => res.json())
                .then(data => {{
                    data.forEach(seat => {{
                        seatsState[seat.seat_id] = seat.status;
                    }});
                    render();
                }});

            // 2. WebSocket connection
            const socket = new WebSocket(
                `ws://${{window.location.host}}/ws/sessions/${{sessionId}}/`
            );

            socket.onopen = () => {{
                console.log("WebSocket connected");
            }};

            socket.onmessage = (event) => {{
                const message = JSON.parse(event.data);
                console.log("message:" + message);
                payload = message.payload;
                const {{ seat_id, state }} = payload;
                seatsState[seat_id] = state;
                render();
            }};

            socket.onclose = () => {{
                console.log("WebSocket disconnected");
            }};
        </script>
    </body>
    </html>
    """
    return HttpResponse(html)