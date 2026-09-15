from django.contrib import admin
from django.urls import path
from pos.views import (
    TxtCreateView, TXTListView, PedidoUpdateView, DespacharProductoView,
    pedidos_por_fecha, estado_impresion, pedidos_esperando_domiciliario,
    ConfirmarRecogidaListView, ConfirmarRecogidaView, EliminarPedidoView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TxtCreateView.as_view(), name='producto_create'),
    path('listar/', TXTListView.as_view(), name='producto_listar'),
    path('editar/<int:pk>/', PedidoUpdateView.as_view(), name='producto_editar'),
    path('despachar/<int:pk>/', DespacharProductoView.as_view(), name='producto_despachar'),
    path('eliminar/<int:pk>/', EliminarPedidoView.as_view(), name='producto_eliminar'),
    path('pedidos-por-fecha/', pedidos_por_fecha, name='pedidos_por_fecha'),
    path('estado-impresion/<int:pk>/', estado_impresion, name='estado_impresion'),
    path('pedidos-esperando-domiciliario/', pedidos_esperando_domiciliario, name='pedidos_esperando_domiciliario'),
    path('confirmar-recogida/', ConfirmarRecogidaListView.as_view(), name='confirmar_recogida'),
    path('confirmar-recogida/<int:pk>/', ConfirmarRecogidaView.as_view(), name='confirmar_recogida_pedido'),

]
