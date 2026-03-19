from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Movie
from .serializers import MovieSerializer
from .pagination import MoviePagination


class MovieListView(APIView):

    @swagger_auto_schema(
        operation_summary="List movies",
        operation_description="Returns a paginated list of movies. Supports search by title.",

        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Filter movies by title",
                type=openapi.TYPE_STRING
            ),
        ],

        responses={200: MovieSerializer(many=True)}
    )
    def get(self, request):
        movies = Movie.objects.all().order_by("title")
        search = request.query_params.get("search")

        if search:
            movies = movies.filter(title__icontains=search)
            
        paginator = MoviePagination()
        page = paginator.paginate_queryset(movies, request, view=self)
        serializer = MovieSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)