from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ProductoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #print("✅ WebSocket conectado:", self.scope["client"])
        await self.channel_layer.group_add('productos', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        #print("❌ WebSocket desconectado:", self.scope["client"])
        await self.channel_layer.group_discard('productos', self.channel_name)

    async def producto_actualizado(self, event):
        #print("📦 Mensaje recibido: producto_actualizado", event)
        await self.send(text_data=json.dumps(event['producto']))

    async def actualizar_fecha(self, event):
        #print("📅 Mensaje recibido: actualizar_fecha", event)
        await self.send(text_data=json.dumps({
            "tipo": "actualizar_fecha",
            "fecha": event["fecha"]
        }))

