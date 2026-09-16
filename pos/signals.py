# pos/signals.py
import asyncio
try:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except AttributeError:
    pass

import logging

from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from django.core.cache import cache
from .models import Producto
from .background import background_executor
from .cache_keys import PEDIDOS_ESPERANDO_DOMICILIARIO
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.timezone import localtime, make_aware, is_naive
from django.utils import timezone  # importante para make_aware

logger = logging.getLogger(__name__)


def _enviar_notificacion(fecha_str):
    """
    Corre en el pool de hilos en segundo plano, SIEMPRE. Guardar un
    pedido (lo que el celular esta esperando) nunca debe quedar atado a
    que el aviso por websocket funcione rapido o funcione siquiera. Si
    el channel layer falla o se demora, aqui queda contenido y no
    afecta a nadie mas que esta usando el sistema al mismo tiempo.

    Un solo tipo de mensaje ('actualizar_fecha'): antes se mandaban dos
    (tambien 'producto_actualizado'), pero ningun cliente lo usaba para
    nada -- solo generaba una peticion extra de refresco por cada
    guardado. Con uno solo alcanza para que el frontend sepa "algo
    cambio en esta fecha" y vuelva a pedir esa porcion de la lista.
    """
    try:
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(
            'productos',
            {
                'type': 'actualizar_fecha',
                'fecha': fecha_str,
            }
        )
    except Exception as e:
        logger.warning(
            "Error notificando por websocket (no afecta el guardado del pedido): %s",
            e,
        )


@receiver(post_save, sender=Producto)
def notificar_producto(sender, instance, created, **kwargs):
    fecha = instance.creado_en
    if is_naive(fecha):
        fecha = make_aware(fecha, timezone.get_default_timezone())
    fecha_str = localtime(fecha).date().isoformat()

    # Punto clave: la notificacion se programa con transaction.on_commit,
    # NO se lanza directamente aqui. post_save se dispara justo despues del
    # INSERT/UPDATE en la base, pero ANTES de que la transaccion haga commit
    # si el .save() ocurrio dentro de un `with transaction.atomic():`. Si se
    # avisara de una vez, un cliente podria recibir el mensaje por WS, hacer
    # su fetch() de inmediato, y consultar una fila que tecnicamente todavia
    # no esta comprometida en la base (dato viejo o inexistente).
    #
    # transaction.on_commit() garantiza que esto solo se ejecute cuando la
    # transaccion ya cerro en firme. Si no hay ninguna transaccion abierta
    # (modo autocommit normal, que es lo que se usa hoy en las vistas), Django
    # lo ejecuta inmediatamente despues del save(), como pasaba antes.
    #
    # Ademas, el envio real sigue sin bloquear: se manda al pool de hilos
    # acotado (background_executor) para que ni el .save() ni el on_commit
    # esperen a que el websocket responda.
    def _al_confirmar_commit():
        # Se invalida el fragmento cacheado de "domicilios esperando
        # mensajero" ANTES de avisar por WS -- así, para cuando el
        # navegador reciba el aviso y vuelva a pedirlo, ya encuentra la
        # version fresca (no la vieja que seguia en cache).
        cache.delete(PEDIDOS_ESPERANDO_DOMICILIARIO)
        background_executor.submit(_enviar_notificacion, fecha_str)

    transaction.on_commit(_al_confirmar_commit)
