# pos/server_instance.py
import uuid

# Un ID nuevo cada vez que el proceso del servidor arranca -- se genera
# una sola vez, al importar este modulo, y eso solo pasa una vez por
# proceso (mientras corre, sigue siendo el mismo).
#
# Sirve para que el navegador distinga dos cosas que se ven igual desde
# afuera ("el websocket se desconecto y se volvio a conectar"):
#   1) Se cayo el wifi un momento y el MISMO servidor sigue corriendo.
#   2) El servidor realmente se reinicio (deploy nuevo, se cayo y lo
#      volvieron a prender, reinicio manual).
#
# En el caso 2, las pantallas conectadas pueden estar corriendo HTML/JS
# viejo; se les avisa para que se recarguen solas y traigan lo nuevo.
INSTANCE_ID = uuid.uuid4().hex
