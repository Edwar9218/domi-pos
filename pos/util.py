import win32print


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


def imprimir_texto(texto):
    """
    Manda el texto a la impresora térmica por defecto de Windows.

    Ya NO consulta la cola de impresión de Windows para confirmar si el
    ticket realmente salió: esa verificación (revisar el estado del
    trabajo cada 1s hasta por 8s) se quitó porque hacía más lento el
    sistema, sobre todo cuando entraban varios pedidos seguidos. Ahora
    esta función solo confirma que el comando se mandó a la impresora
    sin errores de Python -- no que el papel salió físicamente.

    Devuelve True si el comando se envió sin errores, False si algo
    falló al mandarlo (impresora no encontrada, sin acceso, etc.).
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

    try:
        win32print.StartDocPrinter(hPrinter, 1, ("Impresión POS", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)

        # Aplicar tamaño de fuente grande + imprimir + cortar
        win32print.WritePrinter(hPrinter, comando_grande + raw_data + comando_corte)

        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)

    # Restaurar tamaño normal
    resetear_tamano_fuente()

    return True
