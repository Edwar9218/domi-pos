# app/signals.py
import asyncio
try:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except AttributeError:
    pass

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Producto
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.timezone import localtime, make_aware, is_naive
from django.utils import timezone  # importante para make_aware

@receiver(post_save, sender=Producto)
def notificar_producto(sender, instance, created, **kwargs):
    
    print("SEÑAL post_save activada")
    print("Producto:", instance)
    print("Fecha:", instance.creado_en)

    layer = get_channel_layer()

    # Enviar actualización normal del producto
    async_to_sync(layer.group_send)(
        'productos',
        {
            'type': 'producto_actualizado',
            'producto': {
                'id': instance.id,
                'txt': instance.txt,
                'despachado': instance.despachado
            }
        }
    )

    # Asegurar que la fecha tenga zona horaria
    fecha = instance.creado_en
    if is_naive(fecha):
        fecha = make_aware(fecha, timezone.get_default_timezone())

    fecha_str = localtime(fecha).date().isoformat()

    # Enviar actualización solo del grupo de esa fecha
    async_to_sync(layer.group_send)(
        'productos',
        {
            'type': 'actualizar_fecha',
            'fecha': fecha_str
        }
    )
