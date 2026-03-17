from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Movie
from .serializers import MovieSerializer
from .pagination import MoviePagination


class MovieListView(APIView):

    def get(self, request):
        movies = Movie.objects.all().order_by("title")
        search = request.query_params.get("search")

        if search:
            movies = movies.filter(title__icontains=search)
            
        paginator = MoviePagination()
        page = paginator.paginate_queryset(movies, request, view=self)
        serializer = MovieSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)