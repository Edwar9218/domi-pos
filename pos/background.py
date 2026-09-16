# pos/background.py
"""
Pool de hilos ACOTADO y compartido para tareas en segundo plano
(notificar por WebSocket, imprimir el ticket, etc.).

Antes cada guardado de un Producto lanzaba su propio
`threading.Thread(...).start()`, sin ningún límite. En uso normal no se
nota, pero bajo ráfagas de guardados (varios pedidos casi simultáneos,
o el propio flujo de "guardar -> imprimir -> guardar de nuevo" que ya
crea dos hilos por pedido) se pueden ir acumulando hilos del sistema
operativo sin control.

Con un ThreadPoolExecutor de tamaño fijo, las tareas se encolan y se
ejecutan con un número máximo de hilos reutilizables. Sigue sin
bloquear la petición HTTP/señal que las dispara (submit() es
no-bloqueante), pero ahora con un límite claro y predecible.
"""
from concurrent.futures import ThreadPoolExecutor

# 8 hilos es de sobra para esta app (notificar WS es casi instantáneo,
# imprimir tarda unos segundos como mucho) y evita que un pico de
# pedidos dispare decenas de hilos nuevos al mismo tiempo.
background_executor = ThreadPoolExecutor(
    max_workers=8,
    thread_name_prefix="domi-pos-bg",
)
