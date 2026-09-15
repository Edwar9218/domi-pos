import os
import django
from concurrent.futures import ThreadPoolExecutor
from asgiref.sync import SyncToAsync
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import pos.routing    # <— import correcto de tu app "pos"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# 🔴 Por defecto, Django sobre un servidor ASGI (Daphne) atiende TODAS
# las vistas normales (no-async) en un único hilo, una detrás de otra.
# Con varias pantallas conectadas a la vez (celular, cocina, confirmar
# recogida) eso significa que una petición un poco lenta bloquea a
# TODAS las demás mientras espera su turno. Se amplía el pool de hilos
# para que varias peticiones se puedan atender en paralelo de verdad.
SyncToAsync.single_thread_executor = ThreadPoolExecutor(max_workers=20)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(pos.routing.websocket_urlpatterns)
    ),
})
