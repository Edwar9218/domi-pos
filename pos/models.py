from django.db import models

# Create your models here.
class Producto(models.Model):
    txt = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    despachado = models.BooleanField(default=False)
    def __str__(self):
        return self.txt