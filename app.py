"""
EDA - Mercado laboral colombiano — landing page dinámica en Dash.
Corre con: python app.py  (sirve en http://127.0.0.1:8060)
"""
from dash import Dash, html

import figures as f
from data_loader import build_dataset
from layout import (autores_layout, biblio_layout, eda_layout, intro_layout,
                     make_footer, make_header, make_tabs)

data = build_dataset()

figs = {
    "hist_target": f.fig_hist_target(data),
    "box_target": f.fig_box_target(data),
    "box_allvars": f.fig_box_allvars(data),
    "corr": f.fig_corr(data),
    "vif": f.fig_vif(data),
    "scatter_feature": f.fig_scatter_feature(data),
    "evolucion": f.fig_evolucion(data),
    "box_anual_des": f.fig_box_anual(data, "tasa_desempleo_nacional", "#e0a3a3", "Desempleo — Distribución anual"),
    "box_anual_ocu": f.fig_box_anual(data, "tasa_ocupacion_nacional", "#6f9bd1", "Ocupación — Distribución anual"),
    "decomp": f.fig_decomp(data),
    "acf_pacf": f.fig_acf_pacf(data),
    "lag_corr": f.fig_lag_corr(data),
}

app = Dash(__name__, title="EDA - Mercado laboral colombiano")
server = app.server

app.layout = html.Div([
    make_header(),
    make_tabs(),
    html.Main([
        intro_layout(data),
        eda_layout(data, figs),
        autores_layout(),
        biblio_layout(),
    ]),
    make_footer(),
])

if __name__ == "__main__":
    app.run(debug=False, port=8060)
