import win32print
from datetime import datetime

import win32print

def resetear_tamano_fuente():
    comando_normal = b'\x1B\x21\x00'# Tamaño estándar
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


def imprimir_texto(texto):
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

    try:
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Impresión POS", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)

        # Aplicar tamaño de fuente grande + imprimir + cortar
        win32print.WritePrinter(hPrinter, comando_grande + raw_data + comando_corte)

        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)

    # Restaurar tamaño normal
    resetear_tamano_fuente()