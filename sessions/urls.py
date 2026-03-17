from django.urls import path
from .views import MovieSessionListView

urlpatterns = [
    path("movies/<int:movie_id>/sessions/", MovieSessionListView.as_view(), name="movie-sessions"),
]