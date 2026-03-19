from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from datetime import datetime, timedelta, time
from collections import defaultdict

from .models import Session
from .serializers import SessionSerializer
from movies.models import Movie


class MovieSessionListView(APIView):

    @swagger_auto_schema(
        operation_summary="List sessions by movie and date range",
        operation_description=(
            "Returns sessions grouped by date for a given movie. "
            "You can control the start date and number of days."
        ),

        manual_parameters=[
            openapi.Parameter(
                'movie_id',
                openapi.IN_PATH,
                description="ID of the movie",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Start date in format YYYY-MM-DD (default: today)",
                type=openapi.TYPE_STRING,
                format='date'
            ),
            openapi.Parameter(
                'days',
                openapi.IN_QUERY,
                description="Number of days to include (1–30, default: 3)",
                type=openapi.TYPE_INTEGER
            ),
        ],

        responses={
            200: openapi.Response(
                description="Sessions grouped by date",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                        'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                        'days': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'sessions': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="Dictionary where keys are dates (YYYY-MM-DD) and values are lists of sessions"
                        ),
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid parameters (days or date format)"
            ),
            404: openapi.Response(
                description="Movie not found"
            ),
        }
    )
    def get(self, request, movie_id):
        movie = get_object_or_404(Movie, id=movie_id)

        start_date_str = request.query_params.get("start_date")
        days_str = request.query_params.get("days", "3")

        try:
            days = int(days_str)
            if days <= 0 or days > 30:
                raise ValueError
        except ValueError:
            return Response(
                {"detail": "Inválido, days precisa ser de 1 a 30"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if start_date_str:
            try:
                date_obj = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"detail": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            date_obj = timezone.localdate()

        start = timezone.make_aware(datetime.combine(date_obj, time.min))
        end = start + timedelta(days=days)

        queryset = Session.objects.filter(
            movie=movie,
            start_time__gte=start,
            start_time__lt=end
        ).select_related("room").order_by("start_time")

        grouped = defaultdict(list)

        for session in queryset:
            date_key = session.start_time.date().isoformat()
            grouped[date_key].append(session)

        for i in range(days):
            date = (start + timedelta(days=i)).date().isoformat()
            grouped.setdefault(date, [])

        result = {
            date: SessionSerializer(sessions, many=True).data
            for date, sessions in grouped.items()
        }

        result = dict(sorted(result.items()))

        return Response({
            "start_date": date_obj.isoformat(),
            "days": days,
            "end_date": (end - timedelta(days=1)).date().isoformat(),
            "sessions": result
        }, status=status.HTTP_200_OK)