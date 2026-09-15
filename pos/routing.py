from django.urls import re_path
from .consumers import ProductoConsumer

websocket_urlpatterns = [
    re_path(r'^ws/productos/$', ProductoConsumer.as_asgi()),
]
