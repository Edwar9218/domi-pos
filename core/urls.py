from django.contrib import admin
from django.urls import path
from pos.views import TxtCreateView, TXTListView, PedidoUpdateView, DespacharProductoView ,pedidos_por_fecha

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TxtCreateView.as_view(), name='producto_create'),
    path('listar/', TXTListView.as_view(), name='producto_listar'),
    path('editar/<int:pk>/', PedidoUpdateView.as_view(), name='producto_editar'),
    path('despachar/<int:pk>/', DespacharProductoView.as_view(), name='producto_despachar'),
    path('pedidos-por-fecha/', pedidos_por_fecha, name='pedidos_por_fecha'),

]
