# Domi-POS

Sistema en Django para generar y gestionar el papel/recibo que se entrega al domiciliario, con dirección, número de teléfono y demás datos del pedido. Cada pedido generado queda guardado en el sistema para consulta y seguimiento posterior.

## Tecnologías

- **Python 3.11 + Django 4.2**
- **Channels + Daphne** — soporte en tiempo real (websockets) para actualizar pedidos sin recargar la página
- **pywin32** — impresión directa desde Windows del recibo/papel del domiciliario
- **python-dotenv** — manejo de variables de entorno sensibles

## Requisitos previos

- Python 3.11 (o compatible)
- Windows (el módulo de impresión usa `pywin32`, específico de Windows)
- Una impresora configurada en el sistema, si vas a usar la función de impresión directa

## Instalación

1. Clona el repositorio:

   ```
   git clone https://github.com/Edwar9218/domi-pos.git
   cd domi-pos
   ```

2. Crea y activa un entorno virtual (con conda o venv):

   ```
   conda create -n domipos python=3.11
   conda activate domipos
   ```

3. Instala las dependencias:

   ```
   pip install -r requirements.txt
   ```

4. Crea un archivo `.env` en la raíz del proyecto (mismo nivel que `manage.py`) con tu propia clave secreta:

   ```
   SECRET_KEY="pon-aqui-tu-clave-secreta"
   ```

   Puedes generar una clave nueva con:

   ```
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. Aplica las migraciones (esto crea tu propio `db.sqlite3` local, que no se sube al repo):

   ```
   python manage.py migrate
   ```

6. Crea un superusuario para acceder al panel de administración (opcional):

   ```
   python manage.py createsuperuser
   ```

7. Levanta el servidor:
   ```
   python manage.py runserver
   ```

## Notas

- `db.sqlite3`, `datos.json` y `.env` están excluidos del repo (`.gitignore`) porque contienen datos sensibles o específicos de cada máquina. `datos.csv` sí está incluido en el repositorio.
- El módulo de impresión (`win32print`) solo funciona en Windows. Si el proyecto se despliega en un servidor Linux en el futuro, esa parte necesitará adaptarse (por ejemplo, generando el PDF/ticket para imprimir desde el navegador en vez de imprimir directo desde el servidor).
  -marcar como "ya recogido" todo lo histórico (todo lo que ya estaba despachado antes de hoy)
  python manage.py shell -c "from pos.models import Producto; from django.utils import timezone; n = Producto.objects.filter(despachado=True, recogido=False).update(recogido=True, recogido_en=timezone.now()); print(f'{n} pedidos historicos marcados como recogidos')"
