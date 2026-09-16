# Django core views and utilities
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.cache import cache

# Modelos y utilidades locales
from .models import Producto, Cliente
from .forms import ClienteForm
from .util import imprimir_texto
from .background import background_executor
from .cache_keys import PEDIDOS_ESPERANDO_DOMICILIARIO

# Búsquedas
from django.db.models import Q

# Fechas y zona horaria
from datetime import datetime, date, timedelta
from django.utils.dateparse import parse_date
import pytz


def _imprimir_en_segundo_plano(pedido_id, texto_impresion):
    """
    Corre en segundo plano (pool acotado) para que la petición del celular
    no se quede esperando a la impresora. Ya no consulta la cola de
    Windows para confirmar si el ticket salió físicamente -- eso se quitó
    por ser lento. Guarda el resultado con .save() normal para que dispare
    la señal post_save y así todas las pantallas conectadas (cocina,
    celular) se enteren del cambio en vivo.
    """
    try:
        imprimir_texto(texto_impresion)
        producto = Producto.objects.get(pk=pedido_id)
        producto.impreso = True
        producto.despachado = True
        producto.save()
    except Exception as e:
        print(f"Error al imprimir: {e}")
        try:
            producto = Producto.objects.get(pk=pedido_id)
            producto.impreso = False
            producto.save()
        except Exception as e2:
            print(f"Error guardando estado de impresión fallida: {e2}")

class TxtCreateView(CreateView):
    model = Producto
    fields = ['txt']
    template_name = 'plantillas/pos.html'
    success_url = reverse_lazy('producto_create')

    def form_valid(self, form):
        # Texto que el usuario envió en el POST
        texto_usuario = self.request.POST.get('txt', '').strip()

        # Normalizamos saltos de línea
        texto_usuario_normalizado = texto_usuario.replace("\r\n", "\n")

        # Plantilla por defecto
        texto_final = "----------------------------\nTotal:\ndomicilio:\nPaga el cliente:"

        # Validar si el texto es solo la plantilla (o está vacío)
        if texto_usuario_normalizado.replace(texto_final, "").strip() == "":
            form.add_error('txt', 'Debe ingresar el pedido antes de guardar.')
            return self.form_invalid(form)

        accion = self.request.POST.get("accion")
        #print(self.request.POST)
        if accion == 'imprimir':
            # Preparamos el texto que va a la impresora
            texto = form.instance.txt
            zona_local = pytz.timezone("America/Bogota")  # Ajusta según tu zona
            ahora = datetime.now(zona_local)
            fecha_hora = ahora.strftime("%d/%m/%Y %H:%M:%S")
            texto_impresion = texto + "\n" + f' \n{fecha_hora}'
            texto_impresion = texto_impresion.encode('latin-1', 'ignore').decode('latin-1')

            # Guardamos el pedido YA (impreso=None = "en proceso") para que
            # el celular obtenga respuesta al instante y cocina lo vea aparecer.
            form.instance.impreso = None
            form.instance.despachado = False
            form.instance.save()
            pedido_id = form.instance.pk

            # La impresión real se hace en segundo plano (pool acotado de
            # hilos, compartido con las notificaciones WS), así la petición
            # del celular no se queda "cargando" esperando a la impresora.
            background_executor.submit(
                _imprimir_en_segundo_plano, pedido_id, texto_impresion
            )

            return redirect(f"{reverse('producto_create')}?check={pedido_id}")
        return super().form_valid(form)
    

def _resolver_rango_fechas(request, dias_por_defecto=60):
    """
    Lee ?desde=YYYY-MM-DD&hasta=YYYY-MM-DD de la URL. Si la persona no
    puso ninguno de los dos, usa por defecto los últimos ~2 meses
    (60 días) en vez de traer TODO el historial -- antes esta pantalla
    cargaba años completos de pedidos de una sola vez, lo que la hacía
    cada vez más lenta con el tiempo.

    Si solo puso uno de los dos extremos, se completa el otro con un
    valor razonable. Si los puso al revés (desde > hasta), se invierten
    solos para no romper la consulta.
    """
    hoy = date.today()
    desde = parse_date(request.GET.get("desde") or "")
    hasta = parse_date(request.GET.get("hasta") or "")

    if desde is None and hasta is None:
        hasta = hoy
        desde = hoy - timedelta(days=dias_por_defecto)
    else:
        if hasta is None:
            hasta = hoy
        if desde is None:
            desde = hasta - timedelta(days=dias_por_defecto)
        if desde > hasta:
            desde, hasta = hasta, desde

    return desde, hasta


class TXTListView(ListView):
    model = Producto
    template_name = "plantillas/posListar.html"
    ordering = '-creado_en'

    def get_queryset(self):
        estado = self.request.GET.get("estado", "pendiente")
        if estado == "despachado":
            queryset = Producto.objects.filter(despachado=True)
        else:
            queryset = Producto.objects.filter(despachado=False)

        desde, hasta = _resolver_rango_fechas(self.request)
        queryset = queryset.filter(creado_en__date__gte=desde, creado_en__date__lte=hasta)

        return queryset.order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estado_actual"] = self.request.GET.get("estado", "pendiente")
        context["today_date"] = date.today().strftime('%Y-%m-%d')  # 👈 esto es lo nuevo
        desde, hasta = _resolver_rango_fechas(self.request)
        context["filtro_desde"] = desde.isoformat()
        context["filtro_hasta"] = hasta.isoformat()
        return context


class PedidoUpdateView(UpdateView):
    model = Producto
    fields = ['txt']  # solo el campo editable
    template_name = "editar.html"
    success_url = reverse_lazy('producto_create') 


class DespacharProductoView(View):
    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        desea_imprimir = request.POST.get('imprimir')  # 'si' o 'no'

        if desea_imprimir == 'si':
            try:
                texto = producto.txt 
                # Obtener hora local y formatear
                zona_local = pytz.timezone("America/Bogota")  # Ajusta según tu zona
                ahora = datetime.now(zona_local)
                fecha_hora = ahora.strftime("%d/%m/%Y %H:%M:%S")
                # Agregar dos saltos de línea + fecha y hora
                texto += "\n" +  f' \n{fecha_hora}'
                texto = texto.encode('latin-1', 'ignore').decode('latin-1')
                imprimir_texto(texto)
            except Exception as e:
                print(f"Error al imprimir: {e}")

        producto.despachado = True
        producto.save()
        return redirect(reverse('producto_create'))


class EliminarPedidoView(View):
    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)

        # 🔒 Medida de seguridad del lado del servidor: un pedido ya
        # despachado NUNCA se borra desde aquí, sin importar lo que
        # mande el navegador. Solo se pueden borrar pendientes.
        if producto.despachado:
            return redirect(f"{reverse('producto_listar')}?estado=despachado")

        producto.delete()
        return redirect(f"{reverse('producto_listar')}?estado=pendiente")


def pedidos_por_fecha(request):
    fecha_str = request.GET.get("fecha")
    estado = request.GET.get("estado", "pendiente")

    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return JsonResponse({"error": "Fecha inválida"}, status=400)

    queryset = Producto.objects.filter(creado_en__date=fecha)
    if estado == "despachado":
        queryset = queryset.filter(despachado=True)
    else:
        queryset = queryset.filter(despachado=False)

    html = render_to_string("plantillas/pedidos_fragment.html", {
        "object_list": queryset,
        "today_date": fecha_str,
    })
    return JsonResponse({"html": html})


def pedidos_esperando_domiciliario_html():
    """Genera el HTML de la lista de pedidos despachados que aún no
    ha recogido el domiciliario. Se reutiliza tanto para el primer
    cargue de la página como para las actualizaciones por AJAX.

    Es el endpoint más golpeado de todo el sistema (cada pantalla lo
    pide al cargar, cada 30s de respaldo, y cada vez que llega un aviso
    por WebSocket), así que se cachea. La caché se invalida en
    signals.py apenas cambia CUALQUIER Producto -- no hay un tiempo de
    espera "a ver si ya pasó suficiente", se borra exactamente cuando
    hace falta. El timeout de acá es solo un respaldo por si algún día
    algo guarda un Producto sin pasar por la señal (poco probable, pero
    más vale no depender de que nunca pase).
    """
    html = cache.get(PEDIDOS_ESPERANDO_DOMICILIARIO)
    if html is not None:
        return html

    pedidos = Producto.objects.filter(despachado=True, recogido=False).order_by('creado_en')
    html = render_to_string("plantillas/esperando_domiciliario_fragment.html", {
        "pedidos": pedidos,
    })
    cache.set(PEDIDOS_ESPERANDO_DOMICILIARIO, html, timeout=300)
    return html


def pedidos_esperando_domiciliario(request):
    """La pantalla del celular (donde se escriben los pedidos) consulta
    esto para pintar/actualizar la lista de 'domicilios que no han salido'."""
    return JsonResponse({"html": pedidos_esperando_domiciliario_html()})


class ConfirmarRecogidaListView(ListView):
    """Pantalla para que mesero/cocina marque cuándo el domiciliario
    ya recogió físicamente el pedido."""
    model = Producto
    template_name = "plantillas/confirmar_recogida.html"
    context_object_name = "object_list"

    def get_queryset(self):
        return Producto.objects.filter(despachado=True, recogido=False).order_by('creado_en')


class ConfirmarRecogidaView(View):
    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        producto.recogido = True
        from django.utils import timezone
        producto.recogido_en = timezone.now()
        producto.save()

        # El guardado ya dispara la señal que avisa por WebSocket a
        # todas las pantallas de "Confirmar recogida" abiertas (incluida
        # esta misma), y esas pantallas ya se refrescan solas al recibir
        # el aviso. Si la petición vino por fetch() (ver
        # recogida_fragment.html), no hace falta mandar de vuelta una
        # redirección con el HTML completo de la página -- basta con un
        # OK liviano. Si vino de un <form> normal (JS desactivado, o
        # algo falló al engancharse), se sigue redirigiendo como antes.
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})

        return redirect(reverse('confirmar_recogida'))


# 📍 Direcciones guardadas de clientes -- para no tener que volver a
# preguntar la dirección cada vez que llaman a pedir.

class ClienteListView(ListView):
    model = Cliente
    template_name = "plantillas/clientes_listar.html"
    context_object_name = "clientes"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q)
                | Q(telefono__icontains=q)
                | Q(direccion__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        return context


class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "plantillas/cliente_form.html"
    success_url = reverse_lazy("clientes_listar")


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "plantillas/cliente_form.html"
    success_url = reverse_lazy("clientes_listar")


class ClienteDeleteView(View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        cliente.delete()
        return redirect(reverse("clientes_listar"))
