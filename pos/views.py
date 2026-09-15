# Django core views and utilities
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.template.loader import render_to_string

# Modelos y utilidades locales
from .models import Producto
from .util import imprimir_texto

# Fechas y zona horaria
from datetime import datetime, date
import pytz

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
            #print('impre','/'*10)
            try:
                texto = form.instance.txt 
                # Obtener hora local y formatear
                zona_local = pytz.timezone("America/Bogota")  # Ajusta según tu zona
                ahora = datetime.now(zona_local)
                fecha_hora = ahora.strftime("%d/%m/%Y %H:%M:%S")
                # Agregar dos saltos de línea + fecha y hora
                texto += "\n" +  f' \n{fecha_hora}'
                texto = texto.encode('latin-1', 'ignore').decode('latin-1')
                imprimir_texto(texto)
                # Marcar como despachado y guardar
                form.instance.despachado = True
                form.instance.save()
                return redirect(reverse('producto_create'))
            except Exception as e:
                print(f"Error al imprimir: {e}")
        return super().form_valid(form)
    

class TXTListView(ListView):
    model = Producto
    template_name = "plantillas/posListar.html"
    ordering = '-creado_en'

    def get_queryset(self):
        estado = self.request.GET.get("estado", "pendiente")
        if estado == "despachado":
            return Producto.objects.filter(despachado=True).order_by(self.ordering)
        else:
            return Producto.objects.filter(despachado=False).order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estado_actual"] = self.request.GET.get("estado", "pendiente")
        context["today_date"] = date.today().strftime('%Y-%m-%d')  # 👈 esto es lo nuevo
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
