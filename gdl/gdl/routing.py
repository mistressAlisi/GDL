# routing.py
from django.urls import re_path, path
from game.gdlcore.consumers import GDLTicketStreamConsumer, GDLTicketStoreStreamConsumer

websocket_urlpatterns = [
    path('stream_tickets', GDLTicketStreamConsumer.as_asgi()),
    path('stream_quickpicks', GDLTicketStoreStreamConsumer.as_asgi())
]

# print(websocket_urlpatterns)