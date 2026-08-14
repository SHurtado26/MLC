"""
Genera report_data.js a partir de MLC.xlsx: toda la data numérica que el
reporte HTML interactivo (eda_report.html) necesita para dibujar los
gráficos con Plotly.js en el cliente.
"""
import json
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


def clean(arr):
    """NaN -> None para que json.dumps produzca `null` (Plotly lo entiende como hueco)."""
    return [None if (isinstance(v, float) and np.isnan(v)) else round(float(v), 6) for v in arr]


df = pd.read_excel(DATA_PATH, sheet_name="Series de datos").sort_values("fecha").reset_index(drop=True)
df["fecha_str"] = df["fecha"].dt.strftime("%Y-%m-%d")
df["anio"] = df["fecha"].dt.year

out = {}
out["fecha"] = df["fecha_str"].tolist()
out["series"] = {v: clean(df[v]) for v in ALL_VARS}
out["anio"] = df["anio"].tolist()

# ── Descriptivos ─────────────────────────────────────────────────────────
desc = {}
for v in ALL_VARS:
    s = df[v]
    q1, q3 = s.quantile([0.25, 0.75])
    desc[v] = {
        "n": int(s.count()), "mean": round(s.mean(), 3), "median": round(s.median(), 3),
        "std": round(s.std(), 3), "min": round(s.min(), 3), "max": round(s.max(), 3),
        "q1": round(q1, 3), "q3": round(q3, 3), "iqr": round(q3 - q1, 3),
    }
out["desc_stats"] = desc

out["target_stats"] = {
    "skew": round(float(stats.skew(df[TARGET])), 4),
    "kurtosis": round(float(stats.kurtosis(df[TARGET])), 4),
}

# ── Outliers (IQR) ───────────────────────────────────────────────────────
q1, q3 = df[TARGET].quantile([0.25, 0.75])
iqr = q3 - q1
mask_out = (df[TARGET] < q1 - 1.5 * iqr) | (df[TARGET] > q3 + 1.5 * iqr)
out["outliers"] = [
    {"fecha": r["fecha_str"], "valor": round(r[TARGET], 3)}
    for _, r in df.loc[mask_out].iterrows()
]

# ── Correlación ──────────────────────────────────────────────────────────
corr = df[ALL_VARS].corr(method="pearson")
out["corr_matrix"] = {
    "vars": ALL_VARS,
    "matrix": [[round(float(x), 3) for x in row] for row in corr.values],
}

# ── VIF ───────────────────────────────────────────────────────────────────
X = add_constant(df[FEATURES])
vif_rows = []
for i, col in enumerate(X.columns):
    if col == "const":
        continue
    vif_rows.append({"variable": col, "vif": round(float(variance_inflation_factor(X.values, i)), 2)})
vif_rows.sort(key=lambda r: -r["vif"])
out["vif"] = vif_rows

# ── ADF sobre las 6 series ──────────────────────────────────────────────
adf_rows = []
for v in ALL_VARS:
    res = adfuller(df[v], autolag="AIC")
    adf_rows.append({
        "variable": v, "adf_stat": round(float(res[0]), 4), "p_value": round(float(res[1]), 4),
        "n_lags": int(res[2]), "stationary": bool(res[1] < 0.05),
    })
out["adf"] = adf_rows

# ── Descomposición multiplicativa ───────────────────────────────────────
ts = df.set_index("fecha")[TARGET]
ts.index.freq = "ME"
dec = seasonal_decompose(ts, model="multiplicative", period=12)
out["decomposition"] = {
    "fecha": out["fecha"],
    "observed": clean(dec.observed.values),
    "trend": clean(dec.trend.values),
    "seasonal": clean(dec.seasonal.values),
    "resid": clean(dec.resid.values),
}

# ── ACF / PACF ───────────────────────────────────────────────────────────
nlags = 36
acf_vals, acf_confint = acf(ts, nlags=nlags, alpha=0.05)
pacf_vals, pacf_confint = pacf(ts, nlags=nlags, alpha=0.05)
out["acf"] = {
    "lags": list(range(nlags + 1)),
    "values": clean(acf_vals),
    "conf_lower": clean(acf_confint[:, 0] - acf_vals),
    "conf_upper": clean(acf_confint[:, 1] - acf_vals),
}
out["pacf"] = {
    "lags": list(range(nlags + 1)),
    "values": clean(pacf_vals),
    "conf_lower": clean(pacf_confint[:, 0] - pacf_vals),
    "conf_upper": clean(pacf_confint[:, 1] - pacf_vals),
}

# ── Lags del target y su correlación ────────────────────────────────────
lag_corr = []
for lag in [1, 3, 6, 12]:
    lag_corr.append({"lag": lag, "corr": round(float(df[TARGET].corr(df[TARGET].shift(lag))), 3)})
out["lag_corr"] = lag_corr

# ── Split temporal train/test ───────────────────────────────────────────
cutoff = df["fecha"].max() - pd.DateOffset(months=N_TEST_MONTHS)
train = df[df["fecha"] <= cutoff]
test = df[df["fecha"] > cutoff]
out["train_test"] = {
    "cutoff": cutoff.strftime("%Y-%m-%d"),
    "train_n": int(len(train)), "test_n": int(len(test)),
    "train_start": train["fecha"].min().strftime("%Y-%m-%d"),
    "train_end": train["fecha"].max().strftime("%Y-%m-%d"),
    "test_start": test["fecha"].min().strftime("%Y-%m-%d"),
    "test_end": test["fecha"].max().strftime("%Y-%m-%d"),
}

out["meta"] = {
    "n": int(len(df)), "n_vars": len(ALL_VARS),
    "fecha_min": out["fecha"][0], "fecha_max": out["fecha"][-1],
    "target": TARGET, "features": FEATURES,
}

with open(os.path.join(BASE_DIR, "report_data.js"), "w", encoding="utf-8") as f:
    f.write("const REPORT_DATA = ")
    json.dump(out, f, ensure_ascii=False)
    f.write(";")

print("report_data.js generado.")
