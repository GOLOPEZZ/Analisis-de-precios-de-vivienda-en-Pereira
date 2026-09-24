"""
FASE 2 - Visita cada aviso individual (de la muestra) para sacar el
barrio/zona exacto y confirmar otros datos.

Guarda el progreso poco a poco en fase2_detalle.csv, y si el archivo
ya existe, retoma desde donde se quedó (no vuelve a visitar avisos
que ya estén guardados). Esto es importante porque con ~1500 avisos
y una pausa entre peticiones, el proceso puede tardar más de una
hora - así puedes pausarlo y seguir después sin perder lo avanzado.

Antes de correrlo, asegúrate de haber corrido primero muestreo.py
para generar muestra_fase2.csv
"""

import csv
import os
import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd

ARCHIVO_MUESTRA = "muestra_fase2.csv"
ARCHIVO_SALIDA = "fase2_detalle.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

COLUMNAS_SALIDA = ["url_aviso", "barrio", "precio_detalle", "estado_scraping"]


def cargar_urls_ya_procesadas():
    """Si el archivo de salida ya existe, devuelve el set de URLs que ya tenemos."""
    if not os.path.exists(ARCHIVO_SALIDA):
        return set()
    df_existente = pd.read_csv(ARCHIVO_SALIDA)
    return set(df_existente["url_aviso"].tolist())


def asegurar_archivo_salida():
    """Crea el archivo de salida con encabezados si todavía no existe."""
    if not os.path.exists(ARCHIVO_SALIDA):
        with open(ARCHIVO_SALIDA, "w", newline="", encoding="utf-8-sig") as f:
            escritor = csv.writer(f)
            escritor.writerow(COLUMNAS_SALIDA)


def extraer_texto_o_none(elemento):
    return elemento.get_text(separator=" ", strip=True) if elemento else None


def scrapear_aviso(url):
    """Visita un aviso individual y extrae el barrio y el precio de detalle."""
    respuesta = requests.get(url, headers=HEADERS, timeout=15)

    if respuesta.status_code != 200:
        return {"barrio": None, "precio_detalle": None, "estado_scraping": f"error_http_{respuesta.status_code}"}

    soup = BeautifulSoup(respuesta.text, "html.parser")

    barrio_tag = soup.select_one("span.property-location-tag")
    precio_tag = soup.select_one("p.main-price")

    return {
        "barrio": extraer_texto_o_none(barrio_tag),
        "precio_detalle": extraer_texto_o_none(precio_tag),
        "estado_scraping": "ok",
    }


def main():
    muestra = pd.read_csv(ARCHIVO_MUESTRA)
    urls_ya_procesadas = cargar_urls_ya_procesadas()
    asegurar_archivo_salida()

    urls_pendientes = [
        url for url in muestra["url_aviso"].tolist() if url not in urls_ya_procesadas
    ]

    print(f"Total en la muestra: {len(muestra)}")
    print(f"Ya procesados anteriormente: {len(urls_ya_procesadas)}")
    print(f"Pendientes por procesar ahora: {len(urls_pendientes)}")

    with open(ARCHIVO_SALIDA, "a", newline="", encoding="utf-8-sig") as f:
        escritor = csv.writer(f)

        for indice, url in enumerate(urls_pendientes, start=1):
            try:
                datos = scrapear_aviso(url)
                estado = datos["estado_scraping"]
            except requests.RequestException as e:
                datos = {"barrio": None, "precio_detalle": None, "estado_scraping": "error_conexion"}
                estado = "error_conexion"

            escritor.writerow([url, datos["barrio"], datos["precio_detalle"], estado])
            f.flush()  # aseguramos que quede escrito en disco de una vez

            print(f"[{indice}/{len(urls_pendientes)}] {estado} - {url}")

            time.sleep(random.uniform(1.5, 2.5))

    print("\nListo. Resultados guardados en", ARCHIVO_SALIDA)


if __name__ == "__main__":
    main()
