from channels.generic.websocket import AsyncWebsocketConsumer
import json

from .server_instance import INSTANCE_ID


class ProductoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('productos', self.channel_name)
        await self.accept()

        # Apenas se conecta, se le dice a ESE cliente (no al grupo) con
        # qué instancia del servidor quedó hablando. Si el navegador ve
        # que este ID no coincide con el que tenía guardado de cuando
        # cargó la página, sabe que el servidor se reinició mientras
        # tanto y puede recargarse solo para traer el HTML/JS más
        # reciente.
        await self.send(text_data=json.dumps({
            "tipo": "servidor_id",
            "id": INSTANCE_ID,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('productos', self.channel_name)

    async def actualizar_fecha(self, event):
        # Unico tipo de mensaje que se envia hoy: "algo cambio para esta
        # fecha, vuelve a pedirla". Antes tambien existia
        # 'producto_actualizado', pero ningun cliente lo procesaba -- solo
        # generaba trafico y un refresco extra por cada guardado. Se quito
        # junto con su handler en signals.py.
        await self.send(text_data=json.dumps({
            "tipo": "actualizar_fecha",
            "fecha": event["fecha"]
        }))

    async def receive(self, text_data=None, bytes_data=None):
        """
        Mensajes que llegan DESDE el navegador (no solo los que salen hacia
        el). Hoy el unico que se usa es "escribiendo": el celular lo manda
        mientras alguien esta escribiendo el pedido, solo para comprobar en
        vivo que el viaje de ida y vuelta con el servidor realmente
        funciona -- no para guardar nada.

        Se responde SOLO a quien lo mando (self.send, no group_send), asi
        el texto que alguien esta escribiendo -- todavia sin guardar, puede
        tener datos del cliente a medio escribir -- no se le manda a nadie
        mas conectado al mismo grupo.
        """
        if not text_data:
            return
        try:
            data = json.loads(text_data)
        except (TypeError, ValueError):
            return

        if data.get("tipo") == "escribiendo":
            await self.send(text_data=json.dumps({"tipo": "escribiendo_ack"}))
