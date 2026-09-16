from django.db import migrations


def copiar_telefonos_existentes(apps, schema_editor):
    """
    Antes de quitar el campo Cliente.telefono, esto copia cualquier
    número que ya estuviera guardado ahí hacia el nuevo modelo Telefono
    -- para que nadie pierda un número que ya había registrado.
    """
    Cliente = apps.get_model('pos', 'Cliente')
    Telefono = apps.get_model('pos', 'Telefono')

    for cliente in Cliente.objects.all():
        numero = getattr(cliente, 'telefono', '') or ''
        numero = numero.strip()
        if numero:
            Telefono.objects.create(cliente=cliente, numero=numero)


def revertir(apps, schema_editor):
    # No hay nada sensato que "deshacer" acá (el campo telefono ya no
    # existiría al revertir esta migración de todos modos, porque se
    # quita en la siguiente). No hace falta borrar los Telefono creados.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0006_telefono'),
    ]

    operations = [
        migrations.RunPython(copiar_telefonos_existentes, revertir),
    ]
