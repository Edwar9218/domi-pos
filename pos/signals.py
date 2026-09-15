# app/signals.py
import asyncio
try:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except AttributeError:
    pass

# app/signals.py
import asyncio
try:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except AttributeError:
    pass

import threading

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Producto
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.timezone import localtime, make_aware, is_naive
from django.utils import timezone  # importante para make_aware


def _enviar_notificaciones(producto_id, txt, despachado, fecha_str):
    """
    Corre en un hilo aparte, SIEMPRE. Guardar un pedido (lo que el
    celular está esperando) nunca debe quedar atado a que el aviso
    por websocket funcione rápido o funcione siquiera. Si el channel
    layer falla o se demora, aquí queda contenido y no afecta a nadie
    más que está usando el sistema al mismo tiempo.
    """
    try:
        layer = get_channel_layer()

        async_to_sync(layer.group_send)(
            'productos',
            {
                'type': 'producto_actualizado',
                'producto': {
                    'id': producto_id,
                    'txt': txt,
                    'despachado': despachado,
                }
            }
        )

        async_to_sync(layer.group_send)(
            'productos',
            {
                'type': 'actualizar_fecha',
                'fecha': fecha_str,
            }
        )
    except Exception as e:
        print(f"Error notificando por websocket (no afecta el guardado del pedido): {e}")


@receiver(post_save, sender=Producto)
def notificar_producto(sender, instance, created, **kwargs):
    print("SEÑAL post_save activada")
    print("Producto:", instance)
    print("Fecha:", instance.creado_en)

    fecha = instance.creado_en
    if is_naive(fecha):
        fecha = make_aware(fecha, timezone.get_default_timezone())
    fecha_str = localtime(fecha).date().isoformat()

    # 🔴 Punto clave: NO se espera aquí a que termine el envío por
    # websocket. Se dispara en segundo plano y la señal (y por lo tanto
    # el .save() que la disparó, y la respuesta HTTP al celular) sigue
    # de inmediato, sin importar qué tan rápido o lento ande el socket.
    threading.Thread(
        target=_enviar_notificaciones,
        args=(instance.id, instance.txt, instance.despachado, fecha_str),
        daemon=True,
    ).start()
