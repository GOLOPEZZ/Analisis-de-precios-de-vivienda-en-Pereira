# Analisis-de-precios-de-vivienda-en-Pereira
Un analisis de los precios de vivienda en Pereira, Risaralda utilizando python, Claude y Power BI
# Optimización de precios y demanda inmobiliaria en Pereira, Risaralda

Proyecto de análisis de datos que identifica zonas de Pereira con menor precio por metro cuadrado dentro del mercado de vivienda en venta, mediante web scraping, limpieza de datos en Python y un panel interactivo en Power BI.

## Motivación

Proyecto realizado como pieza de portafolio para demostrar competencias de analista de datos: extracción de datos reales (web scraping), limpieza y transformación (Python/pandas), y visualización de negocio (Power BI).

## Fuente de datos

Avisos de vivienda en venta en Pereira y Risaralda publicados en [Fincaraiz.com.co](https://www.fincaraiz.com.co), uno de los portales inmobiliarios más grandes de Colombia.

- Se respetó el archivo `robots.txt` del sitio, evitando rutas explícitamente prohibidas.
- Se usaron pausas de 1.5–2.5 segundos entre peticiones para no sobrecargar el servidor.
- Los datos se usan exclusivamente con fines educativos/analíticos, sin redistribución comercial.

## Metodología

El proceso se dividió en 3 etapas:

### 1. Scraping del listado (`fase1_scraping_listado.py`)

Recorre las ~365 páginas de resultados de búsqueda de Pereira/Risaralda, extrayendo por cada aviso: precio, tipo de inmueble + ciudad, habitaciones, baños, área, título y la URL del aviso individual. Resultado: **7.637 avisos** (7.460 únicos).

### 2. Muestreo (`muestreo.py`)

Dado el volumen, se tomó una **muestra aleatoria estratificada por página** de ~1.500 avisos, para mantener representatividad geográfica sin necesitar visitar cada uno de los miles de avisos individuales. Resultado: **1.424 avisos** en la muestra.

### 3. Scraping de detalle (`fase2_scraping_detalle.py`)

Visita cada aviso de la muestra para extraer el **barrio exacto** (dato que solo aparece limpio en la página individual, no en la de listado) y confirmar el precio. Incluye manejo de errores HTTP y guardado incremental (permite pausar y reanudar sin perder progreso). Resultado: 1.403 avisos procesados exitosamente.

### 4. Limpieza y análisis (`limpieza_analisis.py`)

- Conversión de campos de texto a numéricos (precio, área, habitaciones, baños).
- Extracción del tipo de inmueble (Apartamento, Casa, Lote, etc.) como campo independiente.
- Cálculo de la métrica central: **precio por metro cuadrado**.
- Filtrado de avisos incompletos o inválidos.
- Resultado final: **1.141 avisos limpios**, listos para Power BI.

## Panel de Power BI

El panel incluye:
- Filtros interactivos por tipo de inmueble y barrio.
- Ranking de barrios por precio/m² promedio (ordenado ascendente, resaltando zonas de menor precio).
- Gráfico de dispersión (área vs. precio) para identificar oportunidades a nivel de aviso individual.
- Tabla de detalle con los datos limpios de cada aviso.
- KPI de referencia: precio/m² promedio de toda la ciudad, para comparar cada barrio contra el promedio general.

## Principales hallazgos

Los barrios con menor precio/m² promedio dentro de la categoría "Apartamento" fueron: Sector Lago Uribe, Ciudadela del Café Sector C y Sector Plaza de Bolívar, todos por debajo del promedio general de la ciudad (~$5.02 millones/m²).

## Decisiones y limitaciones importantes

- **Comparación por tipo de inmueble**: el análisis de "zonas subvaloradas" se restringió a Apartamentos, porque mezclar lotes, casas y apartamentos en el mismo promedio de precio/m² distorsiona la comparación.
- **Tamaño de muestra por barrio**: el resumen por barrio solo incluye barrios con 5 o más avisos en la muestra, para evitar promedios poco confiables basados en 1-2 casos.
- **Precios "Desde $X"**: algunos avisos corresponden a proyectos con varias tipologías de unidad, mostrando el precio de la más económica. Se marcaron con la columna `es_precio_desde` en vez de excluirlos, para que quien use el panel pueda decidir si filtrarlos.
- **Retorno de inversión (ROI)**: el alcance original del proyecto contemplaba identificar zonas con mayor retorno de inversión, lo cual requeriría datos de arriendo (renta anual / precio de compra) que no se incluyeron en esta primera versión por límites de tiempo. **Próxima mejora natural del proyecto**: scrapear también avisos de arriendo en las mismas zonas para calcular un rendimiento (yield) real por barrio.
- **Muestra, no censo**: los resultados representan una muestra aleatoria estratificada del ~19% del total de avisos activos al momento de la extracción, no el mercado completo.

## Herramientas usadas

Python (requests, BeautifulSoup, pandas, Claude) para scraping y limpieza · Power BI para visualización.

## Estructura del repositorio

```
fase1_scraping_listado.py     # Scraping de las páginas de resultados
muestreo.py                   # Muestreo estratificado por página
fase2_scraping_detalle.py     # Scraping de barrio por aviso individual
limpieza_analisis.py          # Limpieza, transformación y análisis
dataset_limpio.csv            # Dataset final usado en Power BI
resumen_por_barrio.csv        # Resumen agregado por barrio
```
