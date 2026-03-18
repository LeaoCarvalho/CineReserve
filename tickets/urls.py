from django.urls import path
from .views import LockSeatView, SessionSeatsView, TakeSeatView

urlpatterns = [
    path("session/<int:session_id>/seat/<int:seat_id>/lock/", LockSeatView.as_view(), name="seat-lock"),
    path("session/<int:session_id>/seats/", SessionSeatsView.as_view(), name="session-seats-list"),
    path("session/<int:session_id>/seat/<int:seat_id>/confirm/", TakeSeatView.as_view(), name="seat-confirm"),
]