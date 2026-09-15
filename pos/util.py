import win32print
import time
from datetime import datetime

# Banderas de estado de trabajo de impresión de la API de Windows
# (ver documentación de win32print / spoolsv: JOB_INFO_1 "Status")
JOB_STATUS_ERROR = 0x00000002
JOB_STATUS_DELETING = 0x00000004
JOB_STATUS_OFFLINE = 0x00000020
JOB_STATUS_PAPEROUT = 0x00000040
JOB_STATUS_PRINTED = 0x00000080
JOB_STATUS_DELETED = 0x00000100
JOB_STATUS_BLOCKED_DEVQ = 0x00000200
JOB_STATUS_USER_INTERVENTION = 0x00000400
JOB_STATUS_RESTART = 0x00000800

# Cualquiera de estas banderas significa que algo salió mal físicamente
# (impresora apagada, sin papel, atascada, necesita intervención, etc.)
BANDERAS_DE_FALLO = (
    JOB_STATUS_ERROR
    | JOB_STATUS_OFFLINE
    | JOB_STATUS_PAPEROUT
    | JOB_STATUS_BLOCKED_DEVQ
    | JOB_STATUS_USER_INTERVENTION
    | JOB_STATUS_DELETED
    | JOB_STATUS_DELETING
)


def resetear_tamano_fuente():
    comando_normal = b'\x1B\x21\x00'  # Tamaño estándar
    printer_name = win32print.GetDefaultPrinter()
    hPrinter = win32print.OpenPrinter(printer_name)

    try:
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Reset Fuente", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, comando_normal)
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)


def _verificar_estado_trabajo(printer_name, job_id, timeout_segundos=8):
    """
    Consulta la cola de impresión de Windows para saber si el trabajo
    realmente salió, o si quedó atascado/con error (impresora apagada,
    sin papel, offline, etc). Revisa cada 1s hasta timeout_segundos.

    Devuelve True si se imprimió, False si falló o quedó pendiente
    (atascado) al cabo del tiempo de espera.
    """
    fin = time.time() + timeout_segundos
    while time.time() < fin:
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            info = win32print.GetJob(hPrinter, job_id, 1)
        except Exception:
            # Ya no está en la cola: normalmente significa que terminó bien
            return True
        finally:
            win32print.ClosePrinter(hPrinter)

        status = info.get('Status', 0)

        if status & BANDERAS_DE_FALLO:
            return False

        if status & JOB_STATUS_PRINTED:
            return True

        # status == 0 en varias impresoras térmicas RAW significa que ya
        # terminó de procesar el trabajo (no siempre marcan JOB_STATUS_PRINTED)
        if status == 0:
            return True

        time.sleep(1)

    # Se acabó el tiempo y el trabajo seguía en la cola sin confirmar
    return False


def imprimir_texto(texto, verificar_impresion=True, timeout_verificacion=8):
    """
    Manda el texto a la impresora térmica por defecto de Windows.
    Si verificar_impresion=True, además consulta la cola de Windows
    para confirmar si el ticket realmente salió (y no solo que el
    comando se envió sin errores de Python).

    ⚠️ LIMITACIÓN REAL (no es un bug): la mayoría de impresoras térmicas
    de recibos NO tienen comunicación bidireccional con Windows. Esto
    significa que si el driver no reporta el problema (algunas veces
    pasa con "sin papel" o "apagada" según el modelo/driver), Windows
    puede marcar el trabajo como completado aunque el papel nunca haya
    salido físicamente. Esta función confirma lo máximo que Windows
    puede confirmar, pero NO es una garantía absoluta al 100% de que
    el papel salió — por eso el mensaje que ve la persona del celular
    dice "se envió sin errores", no "se imprimió con certeza".

    Devuelve True si se imprimió (o si no se pudo verificar y se
    prefiere asumir éxito), False si se detectó un fallo real.
    """
    try:
        raw_data = texto.encode('cp850')
    except UnicodeEncodeError:
        raw_data = texto.encode('utf-8', errors='ignore')

    # Comando para doble altura y doble ancho
    comando_grande = b'\x1B\x21\x30'  # Este también es común
    # Comando de corte de papel
    comando_corte = b'\n\x1D\x56\x42\x10'

    printer_name = win32print.GetDefaultPrinter()
    hPrinter = win32print.OpenPrinter(printer_name)
    job_id = None

    try:
        job_id = win32print.StartDocPrinter(hPrinter, 1, ("Impresión POS", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)

        # Aplicar tamaño de fuente grande + imprimir + cortar
        win32print.WritePrinter(hPrinter, comando_grande + raw_data + comando_corte)

        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)

    # Restaurar tamaño normal
    resetear_tamano_fuente()

    if not verificar_impresion or not job_id:
        return True

    return _verificar_estado_trabajo(printer_name, job_id, timeout_verificacion)
