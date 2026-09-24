"""
LIMPIEZA Y ANÁLISIS - Une los datos de la Fase 1 (muestra) con los de
la Fase 2 (detalle/barrio), limpia los campos de texto a números, y
calcula el precio por m² agrupado por barrio para identificar zonas
con precios más bajos (candidatas a "subvaloradas").

Genera dos archivos:
- dataset_limpio.csv     -> una fila por aviso, con todos los campos
                            numéricos listos para usar en Power BI
- resumen_por_barrio.csv -> una fila por barrio, con estadísticas
                            agregadas (para la primera vista del panel)
"""

import re
import pandas as pd

ARCHIVO_MUESTRA = "muestra_fase2.csv"
ARCHIVO_DETALLE = "fase2_detalle.csv"


def limpiar_precio(texto):
    """'Desde $ 209.740.910' o '$ 720.000.000' -> 209740910 / 720000000 (int)."""
    if pd.isna(texto):
        return None
    solo_numeros = re.sub(r"[^\d]", "", texto)
    if solo_numeros == "":
        return None
    return int(solo_numeros)


def es_precio_desde(texto):
    if pd.isna(texto):
        return False
    return "desde" in texto.lower()


def limpiar_area(texto):
    """'30.45 m²' -> 30.45 (float)."""
    if pd.isna(texto):
        return None
    match = re.search(r"[\d.]+", texto)
    if not match:
        return None
    return float(match.group())


def limpiar_numero_typology(texto):
    """'1 Hab' o '1 Baño' -> 1 (int). Si el texto no trae número, None."""
    if pd.isna(texto):
        return None
    match = re.search(r"\d+", texto)
    if not match:
        return None
    return int(match.group())

def extraer_tipo_inmueble(texto):
    """'Apartamento en Pereira, Risaralda' -> 'Apartamento'."""
    if pd.isna(texto):
        return None
    return texto.split(" en ")[0].strip()

def limpiar_barrio(texto):
    """'Cerritos, Risaralda' -> 'Cerritos'."""
    if pd.isna(texto):
        return None
    return texto.split(",")[0].strip()


def main():
    muestra = pd.read_csv(ARCHIVO_MUESTRA)
    detalle = pd.read_csv(ARCHIVO_DETALLE)

    print(f"Avisos en la muestra: {len(muestra)}")
    print(f"Avisos con resultado de la Fase 2: {len(detalle)}")

    # Unimos ambos archivos por la URL del aviso
    df = muestra.merge(detalle, on="url_aviso", how="inner")
    print(f"Avisos combinados: {len(df)}")

    # Nos quedamos solo con los que se scrapearon sin error
    df = df[df["estado_scraping"] == "ok"]
    print(f"Avisos con estado 'ok': {len(df)}")

    # Limpieza de campos de texto a números
    df["precio"] = df["precio_detalle"].apply(limpiar_precio)
    df["es_precio_desde"] = df["precio_detalle"].apply(es_precio_desde)
    df["area_m2"] = df["area_texto"].apply(limpiar_area)
    df["habitaciones"] = df["habitaciones_texto"].apply(limpiar_numero_typology)
    df["banos"] = df["banos_texto"].apply(limpiar_numero_typology)
    df["barrio"] = df["barrio"].apply(limpiar_barrio)
    df["tipo_inmueble"] = df["tipo_y_ciudad"].apply(extraer_tipo_inmueble)

    # Quitamos filas sin los datos mínimos para el análisis
    antes = len(df)
    df = df.dropna(subset=["precio", "area_m2", "barrio"])
    df = df[df["area_m2"] > 0]  # evita divisiones por cero
    print(f"Se descartaron {antes - len(df)} avisos por datos incompletos o inválidos")

    # La métrica central del proyecto: precio por metro cuadrado
    df["precio_por_m2"] = df["precio"] / df["area_m2"]

    columnas_finales = [
        "url_aviso", "barrio","tipo_inmueble", "tipo_y_ciudad", "precio", "es_precio_desde",
        "area_m2", "precio_por_m2", "habitaciones", "banos", "titulo",
    ]
    df[columnas_finales].to_csv("dataset_limpio.csv", index=False, encoding="utf-8-sig")
    print(f"\nGuardado dataset_limpio.csv con {len(df)} avisos listos para Power BI")

    # Resumen por barrio (solo barrios con al menos 5 avisos, para que el
    # promedio tenga algo de sustento estadístico)
    resumen = (
        df[df["tipo_inmueble"] == "Apartamento"]
        .groupby("barrio")
        .agg(
            cantidad_avisos=("precio_por_m2", "count"),
            precio_m2_promedio=("precio_por_m2", "mean"),
            precio_m2_mediana=("precio_por_m2", "median"),
        )
        .reset_index()
    )
    resumen = resumen[resumen["cantidad_avisos"] >= 5]
    resumen = resumen.sort_values("precio_m2_promedio")

    resumen.to_csv("resumen_por_barrio.csv", index=False, encoding="utf-8-sig")
    print(f"Guardado resumen_por_barrio.csv con {len(resumen)} barrios (con 5+ avisos)")

    print("\nLos 10 barrios con menor precio por m² (candidatos a 'subvalorados'):")
    print(resumen.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
