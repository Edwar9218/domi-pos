from django.core.management.base import BaseCommand
from django.utils import timezone

from pos.models import Producto


class Command(BaseCommand):
    help = (
        "Marca como despachados todos los pedidos pendientes. "
        "Usa --recogidos para además marcarlos como recogidos por el domiciliario. "
        "Como usa .save() por cada pedido, las pantallas de cocina y del "
        "celular que estén abiertas se actualizan solas (websocket)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--recogidos",
            action="store_true",
            help="También marca los pedidos como recogidos por el domiciliario.",
        )
        parser.add_argument(
            "--si",
            action="store_true",
            help="Confirma la acción sin preguntar (para usarlo en scripts automáticos).",
        )

    def handle(self, *args, **options):
        pendientes = Producto.objects.filter(despachado=False)
        total = pendientes.count()

        if total == 0:
            self.stdout.write("No hay pedidos pendientes. No se hizo ningún cambio.")
            return

        if not options["si"]:
            respuesta = input(
                f"Vas a marcar {total} pedido(s) como despachado(s)"
                + (" y recogido(s)" if options["recogidos"] else "")
                + ". ¿Confirmas? (s/n): "
            ).strip().lower()
            if respuesta != "s":
                self.stdout.write("Cancelado. No se hizo ningún cambio.")
                return

        ahora = timezone.now()
        actualizados = 0
        for pedido in pendientes:
            pedido.despachado = True
            if options["recogidos"]:
                pedido.recogido = True
                pedido.recogido_en = ahora
            pedido.save()  # dispara la señal -> notifica por websocket a cocina/celular
            actualizados += 1

        self.stdout.write(self.style.SUCCESS(
            f"{actualizados} pedido(s) marcados como despachados"
            + (" y recogidos" if options["recogidos"] else "") + "."
        ))
