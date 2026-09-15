import pandas as pd
import ast
import unicodedata
import re
from rapidfuzz import fuzz

# ======================================================
# CONFIGURACIÓN
# ======================================================

CSV_PATH = "D:/pos_domi/datos.csv"
COLUMNA_FIELDS = "fields"
FUZZY_THRESHOLD = 85

# ======================================================
# NORMALIZACIÓN DE TEXTO (hecha para TU CSV)
# ======================================================

def normalizar(texto):
    if not isinstance(texto, str):
        return ""

    # arreglar codificación rota común
    try:
        texto = texto.encode("latin1").decode("utf-8")
    except Exception:
        pass

    texto = texto.lower()

    # unir saltos de línea
    texto = texto.replace("\r", " ").replace("\n", " ")

    # números romanos comunes
    texto = re.sub(r'\bii\b', '2', texto)
    texto = re.sub(r'\bi\b', '1', texto)

    # quitar acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')

    # limpiar símbolos
    texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()

    return texto


# ======================================================
# LISTA DE BARRIOS / CORREGIMIENTOS
# (se agregan los que aparecen en tus datos reales)
# ======================================================

barrios_oficiales = [
    "Alameda I", "Alameda II", "El Jardín", "El Palmar", "La Graciela", "La Trinidad",
    "Siete de Agosto", "Villa Colombia", "Internacional", "Juan XXIII", "El Bosquecito",
    "Maracaibo", "Río Paila", "Portales del Río", "Samán del Norte", "Chiminangos",
    "Municipal", "Bello Horizonte", "Bosques de Maracaibo", "Comfamiliar",
    "Americana de Vivienda", "El Refugio", "Flor de la Campana",
    "Horizonte Santa Isabel", "Jorge Eliecer Gaitán", "La Independencia",
    "El Limonar", "San Luis", "Santa Inés de Comfamiliar", "Tercer Milenio",
    "Villa Liliana", "Departamental", "Porvenir", "Farfán", "La Quinta",
    "Las Américas", "Los Tolúes", "Rojas", "El Descanso", "Guayacanes",
    "José Antonio Galán", "Juan de Lemus y Aguirre", "La Campiña", "Las Nieves",
    "Laureles I", "Laureles II", "Nuevo Farfán", "Los Olmos",
    "Prados del Norte", "Rubén Cruz Vélez", "Villa del Sur", "Bolívar",
    "Playas", "Marandúa", "Pueblo Nuevo", "La Ceiba", "La Esperanza",
    "Los Comuneros del Corazón del Valle", "Primero de Mayo", "Las Delicias",

    # NUEVOS (reales en tus datos)
    "Alvernia", "San Marino", "Santa Rita", "Arboledas del Darién",
    "San Benito", "Progresar", "Céspedes", "Victoria", "Aguaclara",

    # Corregimientos
    "Andinápolis", "Barragán", "Ceilán", "La Marina", "Monteloro",
    "Puerto Frazadas", "San Rafael", "Venecia", "San Lorenzo",
    "Campoalegre", "El Retiro", "El Pomo", "El Picacho", "El Tablazo",
    "El Bosque", "El Diamante", "El Recreo", "El Silencio", "La Iberia",
    "La Moralia", "La Rivera", "Las Vegas", "Naranjal", "San Antonio"
]

barrios_norm = {normalizar(b): b for b in barrios_oficiales}

# ======================================================
# ALIAS REALES
# ======================================================

ALIAS_BARRIOS = {
    "7 de agosto": ["Siete de Agosto"],
    "siete agosto": ["Siete de Agosto"],
    "nuevo principe": ["El Príncipe"],
    "principe": ["El Príncipe"],
    "hospital ruben cruz velez": ["Rubén Cruz Vélez"],
    "villaliliana": ["Villa Liliana"],
    "nuevo farfan": ["Nuevo Farfán"],
    "farfan viejo": ["Nuevo Farfán"],
    "bosques maracaibo": ["Bosques de Maracaibo"],
    "las americas": ["Las Américas"],
    "santa ines": ["Santa Inés de Comfamiliar"],
    "alameda 1": ["Alameda I"],
    "alameda 2": ["Alameda II"],
}

# ======================================================
# REGLAS AUXILIARES
# ======================================================

def detectar_barrio_por_regex(texto_norm):
    match = re.search(r'\bbarrio\s+([a-z\s]+)', texto_norm)
    return match.group(1).strip() if match else None


def lineas_candidatas(texto):
    lineas = texto.splitlines()
    buenas = []

    for l in lineas:
        l_norm = normalizar(l)
        if 3 <= len(l_norm) <= 35 and not re.search(r'\d', l_norm):
            buenas.append(l_norm)

    return buenas


# ======================================================
# BUSCADOR DE BARRIO (FINAL)
# ======================================================

def buscar_barrio(texto):
    texto_norm = normalizar(texto)
    encontrados = []

    # 1️⃣ regex "barrio X"
    candidato = detectar_barrio_por_regex(texto_norm)
    if candidato:
        for b_norm, b_orig in barrios_norm.items():
            if candidato in b_norm:
                encontrados.append(b_orig)

    # 2️⃣ líneas cortas
    if not encontrados:
        for l in lineas_candidatas(texto):
            if l in barrios_norm:
                encontrados.append(barrios_norm[l])

    # 3️⃣ coincidencia por palabras
    if not encontrados:
        for b_norm, b_orig in barrios_norm.items():
            if all(p in texto_norm for p in b_norm.split()):
                encontrados.append(b_orig)

    # 4️⃣ fuzzy
    if not encontrados:
        for b_norm, b_orig in barrios_norm.items():
            if fuzz.token_set_ratio(b_norm, texto_norm) >= FUZZY_THRESHOLD:
                encontrados.append(b_orig)

    # 5️⃣ alias
    if not encontrados:
        for alias, barrios in ALIAS_BARRIOS.items():
            if alias in texto_norm:
                encontrados.extend(barrios)

    return list(set(encontrados))


# ======================================================
# PROCESAR CSV
# ======================================================

df = pd.read_csv(CSV_PATH)

filas_con_barrio = 0
filas_sin_barrio = 0

for _, row in df.iterrows():
    try:
        data = ast.literal_eval(row[COLUMNA_FIELDS])
        texto = data.get("txt", "")
        barrios = buscar_barrio(texto)

        if barrios:
            filas_con_barrio += 1
        else:
            filas_sin_barrio += 1

    except Exception:
        filas_sin_barrio += 1


# ======================================================
# RESULTADOS
# ======================================================

print("================================")
print(f"Filas con barrio reconocido: {filas_con_barrio}")
print(f"Filas sin datos claros: {filas_sin_barrio}")
print(f"Total de filas: {len(df)}")
print("================================")
