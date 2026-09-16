from django.db import models
from urllib.parse import quote
import re

# Create your models here.
class Producto(models.Model):
    txt = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    despachado = models.BooleanField(default=False)
    # None = todavía no se intentó / se está imprimiendo ahora mismo
    # True = se imprimió correctamente
    # False = falló la impresión
    impreso = models.BooleanField(null=True, default=None)

    # Confirmación de que el domiciliario YA recogió el pedido físicamente.
    # despachado=True + recogido=False = está listo pero el mensajero no ha llegado.
    recogido = models.BooleanField(default=False)
    recogido_en = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.txt


class Cliente(models.Model):
    """
    Direcciones de clientes guardadas para no tener que volver a
    preguntarlas cada vez que llaman. El Plus Code es lo que se copia
    directo de Google Maps (botón "Compartir" -> el código que aparece,
    ej: "7WCV+2Q Cali, Colombia") -- con eso se arma un link que abre
    la ubicación exacta en Maps, sin necesitar ninguna llave de API.

    Los teléfonos NO van acá directamente -- un cliente puede tener más
    de uno (casa, trabajo, etc.), así que viven en el modelo Telefono de
    abajo, uno por cada número.
    """
    nombre = models.CharField(max_length=150)
    direccion = models.TextField()
    plus_code = models.CharField(
        max_length=150, blank=True,
        help_text="Pega el Plus Code de Google Maps, ej: 7WCV+2Q Cali, Colombia",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def maps_url(self):
        """None si no hay Plus Code guardado (el template no muestra el
        botón de Maps en ese caso)."""
        if not self.plus_code:
            return None
        return f"https://www.google.com/maps/search/?api=1&query={quote(self.plus_code)}"


class Telefono(models.Model):
    """
    Un número de teléfono de un Cliente, con sus propios accesos
    directos de "llamar" y "WhatsApp". Un mismo cliente puede tener
    varios (por eso es un modelo aparte, no un campo suelto).
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='telefonos')
    numero = models.CharField(max_length=30)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.numero

    def _digitos(self):
        """El número tal como se guarda puede traer espacios, guiones,
        etc. (ej: '300 123 4567') -- esto se queda solo con los números."""
        if not self.numero:
            return ""
        return re.sub(r"\D", "", self.numero)

    def tel_url(self):
        """Link tel: para llamar directo -- funciona tal cual, sin
        necesitar el indicativo del país (el celular ya sabe marcar
        números locales)."""
        digitos = self._digitos()
        return f"tel:{digitos}" if digitos else None

    def whatsapp_url(self):
        """Link wa.me para abrir un chat de WhatsApp directo. A
        diferencia de una llamada normal, WhatsApp SÍ necesita el
        indicativo de país completo -- si el número tiene 10 dígitos
        (el formato típico en Colombia, sin indicativo), se le agrega
        el 57 automáticamente. Si ya trae más dígitos, se asume que el
        indicativo ya está incluido y se deja tal cual."""
        digitos = self._digitos()
        if not digitos:
            return None
        if len(digitos) == 10:
            digitos = "57" + digitos
        return f"https://wa.me/{digitos}"