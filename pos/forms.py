from django import forms
from .models import Cliente, Telefono


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "direccion", "plus_code"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del cliente",
            }),
            "direccion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Dirección completa (barrio, casa/apto, referencia...)",
            }),
            "plus_code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: 7WCV+2Q Cali, Colombia",
            }),
        }
        labels = {
            "nombre": "Nombre del cliente",
            "direccion": "Dirección",
            "plus_code": "Plus Code de Google Maps (opcional)",
        }


class TelefonoForm(forms.ModelForm):
    """Formulario chiquito para agregar un número más a un cliente que
    ya existe -- se usa directo en la tarjeta de la lista, sin tener
    que entrar a editar."""
    class Meta:
        model = Telefono
        fields = ["numero"]
        widgets = {
            "numero": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Agregar número...",
            }),
        }
        labels = {"numero": "Número"}
