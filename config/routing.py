from tickets.routing import websocket_urlpatterns as tickets_ws

websocket_urlpatterns = [
    *tickets_ws,
]