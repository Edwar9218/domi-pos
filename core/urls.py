from django.contrib import admin
from django.urls import path
from pos.views import (
    TxtCreateView, TXTListView, PedidoUpdateView, DespacharProductoView,
    pedidos_por_fecha, pedidos_esperando_domiciliario,
    ConfirmarRecogidaListView, ConfirmarRecogidaView, EliminarPedidoView,
    ClienteListView, ClienteCreateView, ClienteUpdateView, ClienteDeleteView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TxtCreateView.as_view(), name='producto_create'),
    path('listar/', TXTListView.as_view(), name='producto_listar'),
    path('editar/<int:pk>/', PedidoUpdateView.as_view(), name='producto_editar'),
    path('despachar/<int:pk>/', DespacharProductoView.as_view(), name='producto_despachar'),
    path('eliminar/<int:pk>/', EliminarPedidoView.as_view(), name='producto_eliminar'),
    path('pedidos-por-fecha/', pedidos_por_fecha, name='pedidos_por_fecha'),
    path('pedidos-esperando-domiciliario/', pedidos_esperando_domiciliario, name='pedidos_esperando_domiciliario'),
    path('confirmar-recogida/', ConfirmarRecogidaListView.as_view(), name='confirmar_recogida'),
    path('confirmar-recogida/<int:pk>/', ConfirmarRecogidaView.as_view(), name='confirmar_recogida_pedido'),

    # 📍 Direcciones guardadas de clientes
    path('clientes/', ClienteListView.as_view(), name='clientes_listar'),
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='cliente_crear'),
    path('clientes/<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente_editar'),
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_eliminar'),
]
