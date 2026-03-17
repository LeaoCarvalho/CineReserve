from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from datetime import datetime, timedelta, time
from collections import defaultdict

from .models import Session
from .serializers import SessionSerializer
from movies.models import Movie


class MovieSessionListView(APIView):

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