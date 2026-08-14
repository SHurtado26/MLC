"""
Carga el dataset MLC.xlsx y calcula todos los estadísticos que usan las
distintas pestañas de la app Dash (app.py). Se ejecuta una sola vez al
arrancar la app; todo lo que devuelve son estructuras de Python listas
para construir figuras Plotly o tarjetas KPI.
"""
import os

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, adfuller, pacf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "MLC.xlsx")

TARGET = "tasa_desempleo_nacional"
FEATURES = [
    "tasa_global_participacion_area",
    "tasa_global_participacion_nacional",
    "tasa_desempleo_area",
    "tasa_ocupacion_area",
    "tasa_ocupacion_nacional",
]
ALL_VARS = [TARGET] + FEATURES
N_TEST_MONTHS = 24

LABELS = {
    "tasa_global_participacion_area": "Participación (área)",
    "tasa_global_participacion_nacional": "Participación (nacional)",
    "tasa_desempleo_area": "Desempleo (área)",
    "tasa_desempleo_nacional": "Desempleo (nacional)",
    "tasa_ocupacion_area": "Ocupación (área)",
    "tasa_ocupacion_nacional": "Ocupación (nacional)",
}


def label(v):
    return LABELS.get(v, v)


def load_data():
    df = pd.read_excel(DATA_PATH, sheet_name="Series de datos").sort_values("fecha").reset_index(drop=True)
    df["anio"] = df["fecha"].dt.year
    return df


def build_dataset():
    """Calcula todo lo necesario para la app y lo devuelve en un solo dict."""
    df = load_data()
    d = {"df": df}

    # ── Descriptivos ─────────────────────────────────────────────────────
    desc = {}
    for v in ALL_VARS:
        s = df[v]
        q1, q3 = s.quantile([0.25, 0.75])
        desc[v] = {
            "n": int(s.count()), "mean": round(s.mean(), 3), "median": round(s.median(), 3),
            "std": round(s.std(), 3), "min": round(s.min(), 3), "max": round(s.max(), 3),
            "q1": round(q1, 3), "q3": round(q3, 3), "iqr": round(q3 - q1, 3),
        }
    d["desc_stats"] = desc

    d["target_stats"] = {
        "skew": round(float(stats.skew(df[TARGET])), 4),
        "kurtosis": round(float(stats.kurtosis(df[TARGET])), 4),
    }

    # ── Outliers (IQR) ───────────────────────────────────────────────────
    q1, q3 = df[TARGET].quantile([0.25, 0.75])
    iqr = q3 - q1
    mask_out = (df[TARGET] < q1 - 1.5 * iqr) | (df[TARGET] > q3 + 1.5 * iqr)
    d["outliers"] = df.loc[mask_out, ["fecha", TARGET]].copy()

    # ── Correlación y VIF ────────────────────────────────────────────────
    d["corr"] = df[ALL_VARS].corr(method="pearson")

    X = add_constant(df[FEATURES])
    vif_rows = []
    for i, col in enumerate(X.columns):
        if col == "const":
            continue
        vif_rows.append({"variable": col, "vif": round(float(variance_inflation_factor(X.values, i)), 2)})
    vif_rows.sort(key=lambda r: r["vif"])
    d["vif"] = vif_rows

    # ── ADF sobre las 6 series ───────────────────────────────────────────
    adf_rows = []
    for v in ALL_VARS:
        res = adfuller(df[v], autolag="AIC")
        adf_rows.append({
            "variable": v, "adf_stat": round(float(res[0]), 4), "p_value": round(float(res[1]), 4),
            "n_lags": int(res[2]), "stationary": bool(res[1] < 0.05),
        })
    d["adf"] = adf_rows

    # ── Descomposición multiplicativa ────────────────────────────────────
    ts = df.set_index("fecha")[TARGET]
    ts.index.freq = "ME"
    d["decomposition"] = seasonal_decompose(ts, model="multiplicative", period=12)
    d["ts"] = ts

    # ── ACF / PACF ───────────────────────────────────────────────────────
    nlags = 36
    acf_vals, _ = acf(ts, nlags=nlags, alpha=0.05)
    pacf_vals, _ = pacf(ts, nlags=nlags, alpha=0.05)
    d["acf"] = {"lags": list(range(nlags + 1)), "values": acf_vals}
    d["pacf"] = {"lags": list(range(nlags + 1)), "values": pacf_vals}

    # ── Lags del target ──────────────────────────────────────────────────
    lag_corr = []
    for lag in [1, 3, 6, 12]:
        lag_corr.append({"lag": lag, "corr": round(float(df[TARGET].corr(df[TARGET].shift(lag))), 3)})
    d["lag_corr"] = lag_corr

    # ── Split temporal train/test ────────────────────────────────────────
    cutoff = df["fecha"].max() - pd.DateOffset(months=N_TEST_MONTHS)
    train = df[df["fecha"] <= cutoff]
    test = df[df["fecha"] > cutoff]
    d["train_test"] = {
        "cutoff": cutoff, "train_n": int(len(train)), "test_n": int(len(test)),
        "train_start": train["fecha"].min(), "train_end": train["fecha"].max(),
        "test_start": test["fecha"].min(), "test_end": test["fecha"].max(),
    }

    # ── Meta ──────────────────────────────────────────────────────────────
    min_idx = df[TARGET].idxmin()
    max_idx = df[TARGET].idxmax()
    d["meta"] = {
        "n": len(df), "n_vars": len(ALL_VARS),
        "fecha_min": df["fecha"].min(), "fecha_max": df["fecha"].max(),
        "target": TARGET, "features": FEATURES,
        "min_val": df.loc[min_idx, TARGET], "min_fecha": df.loc[min_idx, "fecha"],
        "max_val": df.loc[max_idx, TARGET], "max_fecha": df.loc[max_idx, "fecha"],
        "mean_val": df[TARGET].mean(),
    }

    return d
