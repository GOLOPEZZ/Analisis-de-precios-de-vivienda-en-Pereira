"""
FASE 1 - Scraping de las páginas de resultados de Fincaraiz (Pereira, Risaralda)

Qué hace este script:
1. Recorre las páginas de resultados de /venta/pereira/risaralda
2. De cada tarjeta de aviso extrae: precio, tipo+ciudad, habitaciones,
   baños, área en m², título/descripción y la URL del aviso individual
3. Guarda todo en un CSV (fase1_listado.csv) que usaremos en la Fase 2
   para visitar cada aviso y sacar el barrio exacto.

Antes de correrlo:
    pip install requests beautifulsoup4 pandas
"""

import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://www.fincaraiz.com.co/venta/pereira/risaralda"

HEADERS = {
    # Simulamos un navegador real para que el servidor no rechace la petición
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def construir_url_pagina(numero_pagina: int) -> str:
    """Página 1 es la URL base; de la 2 en adelante se agrega /paginaN."""
    if numero_pagina == 1:
        return BASE_URL
    return f"{BASE_URL}/pagina{numero_pagina}"


def extraer_texto_o_none(elemento):
    """Evita que el script se caiga si un elemento no existe en la tarjeta."""
    return elemento.get_text(separator=" ", strip=True) if elemento else None


def parsear_tarjeta(tarjeta):
    """Extrae los datos de una sola tarjeta (div.listingBoxCard)."""
    datos = {}

    # Precio
    precio_tag = tarjeta.select_one("p.main-price")
    datos["precio_texto"] = extraer_texto_o_none(precio_tag)

    # Tipo de inmueble + ciudad (ej: "Apartamento en Pereira, Risaralda")
    location_tag = tarjeta.select_one("strong.lc-location")
    datos["tipo_y_ciudad"] = extraer_texto_o_none(location_tag)

    # Título / descripción (incluye el barrio mezclado en el texto)
    titulo_tag = tarjeta.select_one("h2.lc-title")
    datos["titulo"] = extraer_texto_o_none(titulo_tag)

    # Habitaciones, baños y m² - vienen en orden fijo dentro de lc-typologyTag
    typology_items = tarjeta.select("div.lc-typologyTag span.lc-typologyTag__item strong")
    textos_typology = [extraer_texto_o_none(item) for item in typology_items]

    # Asignamos por posición (si falta alguno, queda en None)
    datos["habitaciones_texto"] = textos_typology[0] if len(textos_typology) > 0 else None
    datos["banos_texto"] = textos_typology[1] if len(textos_typology) > 1 else None
    datos["area_texto"] = textos_typology[2] if len(textos_typology) > 2 else None

    # URL del aviso individual (para la Fase 2)
    link_tag = tarjeta.select_one("a.lc-data")
    if link_tag and link_tag.get("href"):
        href = link_tag["href"]
        # Algunos links pueden venir relativos, los completamos si hace falta
        if href.startswith("/"):
            href = "https://www.fincaraiz.com.co" + href
        datos["url_aviso"] = href
    else:
        datos["url_aviso"] = None

    return datos


def scrapear_todas_las_paginas(max_paginas: int = 200):
    """
    Recorre las páginas de resultados hasta max_paginas, o hasta detectar
    que el sitio ya no avanza (nos empieza a repetir la última página real).
    """
    todos_los_avisos = []
    urls_pagina_anterior = set()

    for numero_pagina in range(1, max_paginas + 1):
        url = construir_url_pagina(numero_pagina)
        print(f"Descargando página {numero_pagina}: {url}")

        respuesta = requests.get(url, headers=HEADERS, timeout=15)

        if respuesta.status_code != 200:
            print(f"  -> Respuesta inesperada ({respuesta.status_code}), deteniendo.")
            break

        soup = BeautifulSoup(respuesta.text, "html.parser")
        tarjetas = soup.select("div.listingBoxCard")

        if not tarjetas:
            print("  -> No se encontraron más tarjetas, fin de los resultados.")
            break

        datos_pagina = [parsear_tarjeta(tarjeta) for tarjeta in tarjetas]
        urls_esta_pagina = {d["url_aviso"] for d in datos_pagina if d["url_aviso"]}

        # Si esta página trae exactamente los mismos avisos que la anterior,
        # el sitio dejó de avanzar: ya llegamos al final real.
        if urls_esta_pagina and urls_esta_pagina == urls_pagina_anterior:
            print("  -> Esta página repite la anterior, fin real de los resultados.")
            break

        print(f"  -> {len(tarjetas)} avisos encontrados en esta página.")

        for datos_aviso in datos_pagina:
            datos_aviso["pagina"] = numero_pagina
            todos_los_avisos.append(datos_aviso)

        urls_pagina_anterior = urls_esta_pagina
        time.sleep(random.uniform(1.5, 2.5))

    return todos_los_avisos


if __name__ == "__main__":
    avisos = scrapear_todas_las_paginas(max_paginas=400)

    df = pd.DataFrame(avisos)
    df.to_csv("fase1_listado.csv", index=False, encoding="utf-8-sig")

    print(f"\nListo. Se guardaron {len(df)} avisos en fase1_listado.csv")
    print(df.head())