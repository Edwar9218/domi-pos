from django.db import models
from urllib.parse import quote

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
    """
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=30, blank=True)
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