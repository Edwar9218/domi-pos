# pos/context_processors.py
from .server_instance import INSTANCE_ID


def server_instance(request):
    """
    Expone el ID de esta instancia del servidor a TODAS las plantillas
    (via context processor), para que el JS de cada pagina pueda guardarlo
    en window.SERVER_INSTANCE_ID al cargar y despues compararlo contra el
    que le llegue por WebSocket -- ver pos/consumers.py y server_instance.py.
    """
    return {"server_instance_id": INSTANCE_ID}
