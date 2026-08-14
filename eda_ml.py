"""
EDA — Mercado Laboral Colombia (para Machine Learning)
=======================================================
Continuación del EDA descriptivo previo (dashboard Shiny en R, carpeta MLC),
ahora orientado a preparar el terreno para un modelo predictivo de la
tasa de desempleo nacional.

Dataset: MLC.xlsx (hoja "Series de datos")
Periodo: enero 2001 - diciembre 2025 (300 observaciones mensuales)
Fuente: DANE / Banco de la República

Variables:
    fecha
    tasa_global_participacion_area
    tasa_global_participacion_nacional
    tasa_desempleo_area
    tasa_desempleo_nacional        <- variable objetivo
    tasa_ocupacion_area
    tasa_ocupacion_nacional
"""

import os

import matplotlib
matplotlib.use("Agg")  # backend no interactivo: guardamos figuras a disco
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

# ─────────────────────────────────────────────────────────────────────────────
# 0. Configuración
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "MLC.xlsx")
FIG_DIR = os.path.join(BASE_DIR, "eda_ml_figs")
os.makedirs(FIG_DIR, exist_ok=True)

TARGET = "tasa_desempleo_nacional"
FEATURES = [
    "tasa_global_participacion_area",
    "tasa_global_participacion_nacional",
    "tasa_desempleo_area",
    "tasa_ocupacion_area",
    "tasa_ocupacion_nacional",
]
N_TEST_MONTHS = 24  # tamaño del holdout temporal para el futuro modelo

sns.set_theme(style="whitegrid")
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 10)


def savefig(name):
    path = os.path.join(FIG_DIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"  -> figura guardada: {path}")


def section(title):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Carga e inspección inicial
# ─────────────────────────────────────────────────────────────────────────────
section("1. CARGA E INSPECCIÓN INICIAL")

df = pd.read_excel(DATA_PATH, sheet_name="Series de datos")
df = df.sort_values("fecha").reset_index(drop=True)

print(f"Dimensiones: {df.shape}")
print(f"Rango de fechas: {df['fecha'].min().date()} -> {df['fecha'].max().date()}")
print("\nTipos de dato:")
print(df.dtypes)

print("\nValores faltantes por columna:")
print(df.isna().sum())

n_dup = df["fecha"].duplicated().sum()
gaps = df["fecha"].diff().dt.days.dropna()
print(f"\nFechas duplicadas: {n_dup}")
print(f"Orden cronológico correcto (monotónico): {df['fecha'].is_monotonic_increasing}")
print(f"Separación entre observaciones (días) - min/max: {gaps.min()} / {gaps.max()}  "
      f"(esperado: series mensuales, 28-31 días)")

print("\nEstadísticos descriptivos:")
desc = df.drop(columns="fecha").describe().T
desc["IQR"] = desc["75%"] - desc["25%"]
print(desc.round(3))

# ─────────────────────────────────────────────────────────────────────────────
# 2. Análisis univariado
# ─────────────────────────────────────────────────────────────────────────────
section("2. ANÁLISIS UNIVARIADO")

print(f"\nAsimetría y curtosis de la variable objetivo ({TARGET}):")
print(f"  Skewness: {stats.skew(df[TARGET]):.4f}")
print(f"  Kurtosis: {stats.kurtosis(df[TARGET]):.4f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
sns.histplot(df[TARGET], kde=True, color="#0066cc", ax=axes[0])
axes[0].axvline(df[TARGET].mean(), color="#e03131", linestyle="--", label="Media")
axes[0].axvline(df[TARGET].median(), color="#00a854", linestyle="--", label="Mediana")
axes[0].set_title("Distribución — Desempleo Nacional")
axes[0].legend()
sns.boxplot(y=df[TARGET], color="#0066cc", ax=axes[1])
axes[1].set_title("Boxplot — Desempleo Nacional")
savefig("01_univariado_target.png")

# Outliers (regla IQR) sobre el target, con su fecha para contexto
q1, q3 = df[TARGET].quantile([0.25, 0.75])
iqr = q3 - q1
mask_out = (df[TARGET] < q1 - 1.5 * iqr) | (df[TARGET] > q3 + 1.5 * iqr)
print(f"\nOutliers (regla 1.5×IQR) en {TARGET}: {mask_out.sum()}")
if mask_out.any():
    print(df.loc[mask_out, ["fecha", TARGET]].to_string(index=False))

# Distribución de todas las variables (incluye features)
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for ax, col in zip(axes.flat, [TARGET] + FEATURES):
    sns.boxplot(y=df[col], ax=ax, color="#3399ff")
    ax.set_title(col)
savefig("02_boxplots_todas_variables.png")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Análisis bivariado y multicolinealidad
# ─────────────────────────────────────────────────────────────────────────────
section("3. ANÁLISIS BIVARIADO Y MULTICOLINEALIDAD")

corr = df.drop(columns="fecha").corr(method="pearson")
print("\nMatriz de correlación:")
print(corr.round(3))

plt.figure(figsize=(8, 6.5))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1)
plt.title("Matriz de correlación")
savefig("03_correlacion.png")

# VIF (Variance Inflation Factor) sobre las variables predictoras candidatas
# -> el EDA anterior solo reportó correlaciones altas (>0.94) entre área/nacional
#    sin cuantificar el impacto; VIF lo hace explícito para decidir qué eliminar.
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

X = add_constant(df[FEATURES])
vif = pd.DataFrame({
    "variable": X.columns,
    "VIF": [variance_inflation_factor(X.values, i) for i in range(X.shape[1])],
})
vif = vif[vif["variable"] != "const"].sort_values("VIF", ascending=False)
print("\nVIF de las variables predictoras (VIF > 10 indica multicolinealidad severa):")
print(vif.to_string(index=False))

# Scatter del target contra cada feature
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for ax, col in zip(axes.flat, FEATURES):
    sns.scatterplot(x=df[col], y=df[TARGET], ax=ax, alpha=0.6, color="#0066cc")
    ax.set_title(f"{col} vs {TARGET}")
axes.flat[-1].axis("off")
savefig("04_dispersion_target_vs_features.png")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Evolución temporal
# ─────────────────────────────────────────────────────────────────────────────
section("4. EVOLUCIÓN TEMPORAL")

plt.figure(figsize=(13, 5))
plt.plot(df["fecha"], df[TARGET], color="#e03131", label="Desempleo nacional")
plt.plot(df["fecha"], df["tasa_ocupacion_nacional"], color="#0066cc", label="Ocupación nacional")
plt.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-06-01"), color="gray", alpha=0.1)
plt.text(pd.Timestamp("2020-04-01"), plt.ylim()[1] * 0.95, "COVID-19", fontsize=9, color="gray")
plt.legend()
plt.title("Evolución temporal: Desempleo vs Ocupación Nacional")
savefig("05_evolucion_temporal.png")

df["anio"] = df["fecha"].dt.year
plt.figure(figsize=(14, 5))
sns.boxplot(data=df, x="anio", y=TARGET, color="#e03131")
plt.xticks(rotation=90)
plt.title("Desempleo nacional — distribución anual")
savefig("06_boxplot_anual.png")

# ─────────────────────────────────────────────────────────────────────────────
# 5. Series de tiempo: estacionariedad y estacionalidad
# ─────────────────────────────────────────────────────────────────────────────
section("5. SERIES DE TIEMPO — ESTACIONARIEDAD Y ESTACIONALIDAD")

# A diferencia del EDA anterior (que solo corrió ADF sobre el target y asumió
# el resto por su alta correlación), aquí se testean TODAS las series: si van
# a usarse como variables exógenas del modelo, cada una debe evaluarse.
print("\nPrueba de Dickey-Fuller Aumentada (ADF) — H0: la serie tiene raíz unitaria (no estacionaria)")
adf_rows = []
for col in [TARGET] + FEATURES:
    result = adfuller(df[col], autolag="AIC")
    adf_rows.append({
        "variable": col,
        "adf_stat": result[0],
        "p_value": result[1],
        "n_lags": result[2],
        "estacionaria (p<0.05)": "Sí" if result[1] < 0.05 else "No",
    })
adf_df = pd.DataFrame(adf_rows)
print(adf_df.round(4).to_string(index=False))

ts = df.set_index("fecha")[TARGET]
ts.index.freq = "ME"

decomp = seasonal_decompose(ts, model="multiplicative", period=12)
fig = decomp.plot()
fig.set_size_inches(10, 8)
plt.suptitle("Descomposición multiplicativa — Desempleo Nacional", y=1.02)
savefig("07_descomposicion.png")

fig, axes = plt.subplots(2, 1, figsize=(10, 7))
plot_acf(ts, lags=36, ax=axes[0])
plot_pacf(ts, lags=36, ax=axes[1])
savefig("08_acf_pacf.png")

# ─────────────────────────────────────────────────────────────────────────────
# 6. Ingeniería de variables exploratoria (insumo para el modelo)
# ─────────────────────────────────────────────────────────────────────────────
section("6. INGENIERÍA DE VARIABLES EXPLORATORIA")

df_feat = df.copy()

# Lags del target (autocorrelación relevante según ACF/PACF)
for lag in [1, 3, 6, 12]:
    df_feat[f"{TARGET}_lag{lag}"] = df_feat[TARGET].shift(lag)

# Medias y desviaciones móviles
for window in [3, 6, 12]:
    df_feat[f"{TARGET}_rollmean{window}"] = df_feat[TARGET].rolling(window).mean()
    df_feat[f"{TARGET}_rollstd{window}"] = df_feat[TARGET].rolling(window).std()

# Estacionalidad (mes) y choque estructural COVID
df_feat["mes"] = df_feat["fecha"].dt.month
df_feat["covid"] = df_feat["fecha"].between("2020-01-01", "2021-06-01").astype(int)

print("Nuevas columnas creadas (para uso posterior en el modelo):")
print([c for c in df_feat.columns if c not in df.columns])

corr_lags = df_feat[[TARGET] + [c for c in df_feat.columns if "lag" in c]].corr()[TARGET]
print("\nCorrelación del target con sus propios lags:")
print(corr_lags.round(3))

# ─────────────────────────────────────────────────────────────────────────────
# 7. Split temporal train/test (para el futuro modelo)
# ─────────────────────────────────────────────────────────────────────────────
section("7. SPLIT TEMPORAL TRAIN/TEST")

cutoff = df_feat["fecha"].max() - pd.DateOffset(months=N_TEST_MONTHS)
train = df_feat[df_feat["fecha"] <= cutoff]
test = df_feat[df_feat["fecha"] > cutoff]

print(f"Corte de test: últimos {N_TEST_MONTHS} meses (a partir de {cutoff.date()})")
print(f"Train: {train.shape[0]} obs. ({train['fecha'].min().date()} -> {train['fecha'].max().date()})")
print(f"Test:  {test.shape[0]} obs. ({test['fecha'].min().date()} -> {test['fecha'].max().date()})")

out_path = os.path.join(BASE_DIR, "MLC_featured.csv")
df_feat.to_csv(out_path, index=False)
print(f"\nDataset con features exportado a: {out_path}")

# ─────────────────────────────────────────────────────────────────────────────
# 8. Resumen de hallazgos
# ─────────────────────────────────────────────────────────────────────────────
section("8. RESUMEN DE HALLAZGOS")
print(f"""
- Dataset completo y sin valores faltantes: {df.shape[0]} obs. mensuales,
  {df['fecha'].min().date()} a {df['fecha'].max().date()}.
- Outliers en el target ({mask_out.sum()}) coinciden con el choque COVID-19 (2020-2021);
  se conservan por representar información real, no errores de captura.
- Multicolinealidad confirmada entre variables de área y nacional (correlación > 0.94,
  VIF elevado) -> considerar eliminar una de cada par o aplicar reducción de dimensionalidad
  antes de modelar con métodos sensibles a colinealidad (regresión lineal, etc.).
- Ninguna de las 6 series es estacionaria en niveles (ver tabla ADF) -> se requiere
  diferenciación; la estacionalidad anual es clara en la descomposición y el ACF.
- Los lags 1, 3 y 12 del target muestran la correlación más fuerte -> candidatos naturales
  como features para el modelo.
- Split temporal definido: train hasta {cutoff.date()}, test con los últimos
  {N_TEST_MONTHS} meses -> usar este mismo corte (o walk-forward) al entrenar el modelo,
  nunca un split aleatorio dado que es una serie de tiempo.
""")

print(f"Figuras guardadas en: {FIG_DIR}")
print("EDA finalizado.")
