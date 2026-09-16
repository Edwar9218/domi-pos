# pos/cache_keys.py
"""
Claves de cache compartidas entre views.py y signals.py -- en un modulo
aparte para que ambos las importen sin crear un import circular entre
ellos.
"""

PEDIDOS_ESPERANDO_DOMICILIARIO = "pedidos_esperando_domiciliario_html"
