from django.db import models

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