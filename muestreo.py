"""
Toma una muestra representativa de fase1_listado.csv, repartida
proporcionalmente entre todas las páginas, para usar en la Fase 2
(visitar cada aviso individual).
"""

import pandas as pd

TAMANO_MUESTRA_OBJETIVO = 1500
SEMILLA_ALEATORIA = 42  # fija la "aleatoriedad" para que el resultado sea reproducible

df = pd.read_csv("fase1_listado.csv")
print(f"Total de avisos en fase1_listado.csv: {len(df)}")

# Quitamos avisos sin URL (no los podríamos visitar en la Fase 2)
df = df[df["url_aviso"].notna()]

# Quitamos posibles avisos duplicados (mismo url_aviso repetido en distintas páginas)
df = df.drop_duplicates(subset="url_aviso")
print(f"Avisos únicos con URL válida: {len(df)}")

# Muestreo estratificado: tomamos la misma proporción de cada página,
# para que la muestra final quede repartida entre todo el sitio y no
# sesgada hacia las primeras páginas.
fraccion = TAMANO_MUESTRA_OBJETIVO / len(df)

muestra = (
    df.groupby("pagina", group_keys=False)
    .apply(lambda grupo: grupo.sample(frac=fraccion, random_state=SEMILLA_ALEATORIA))
)

print(f"Tamaño final de la muestra: {len(muestra)}")

muestra.to_csv("muestra_fase2.csv", index=False, encoding="utf-8-sig")
print("Guardado en muestra_fase2.csv")
