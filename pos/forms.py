from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "telefono", "direccion", "plus_code"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del cliente",
            }),
            "telefono": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: 300 123 4567",
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
            "telefono": "Teléfono (opcional)",
            "direccion": "Dirección",
            "plus_code": "Plus Code de Google Maps (opcional)",
        }
