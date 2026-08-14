"""Construcción de los layouts Dash (html.Div) de cada pestaña."""
from dash import dcc, html

import theme as t
from data_loader import FEATURES, TARGET, label

PLOTLY_CONFIG = t.PLOTLY_CONFIG


# ── Helpers ──────────────────────────────────────────────────────────────
def kpi_card(label_txt, value, sub=None, variant=None):
    cls = "kpi" + (f" {variant}" if variant else "")
    children = [html.Span(label_txt), html.B(value)]
    if sub:
        children.append(html.Span(sub))
    return html.Div(children, className=cls)


def chart_card(chart_id, figure, interpretation):
    return html.Div([
        dcc.Graph(id=chart_id, figure=figure, config=PLOTLY_CONFIG, className="chart-plot"),
        html.Button("i", className="info-fab", **{"data-target": f"info_{chart_id}"}),
        html.Div([
            html.Span("Interpretación", className="info-label"),
            html.P(interpretation),
        ], className="info-pop", id=f"info_{chart_id}"),
    ], className="chart-card")


def fmt_date(d):
    return d.strftime("%Y-%m-%d")


def fmt_pct(v):
    return f"{v:.2f}%"


# ── Header + Tabs (compartidos) ─────────────────────────────────────────
def make_header():
    return html.Header([
        html.Div([
            html.Div([
                html.Img(src="/assets/banrep_logo.png", className="logo-img", title="Banco de la República"),
            ], className="logo-badge logo-badge-left", id="logoBanrep"),
            html.Div([
                html.H1("EDA - Mercado laboral colombiano"),
                html.P([
                    "DANE / Banco de la República · 300 obs. mensuales · ene 2001 – dic 2025 · preparación para Machine Learning ",
                    html.Img(src="/assets/bandera_colombia.png", className="flag-icon", title="Colombia"),
                ]),
            ], className="header-text"),
            html.Div([
                html.Img(src="/assets/un_logo.png", className="logo-img", title="Universidad del Norte"),
            ], className="logo-badge", id="logoUn"),
        ], className="header-inner"),
    ])


def make_tabs():
    return html.Nav([
        html.Div([
            html.Button("Introducción", className="tab-btn active", id="tab-btn-intro", n_clicks=0),
            html.Button("EDA", className="tab-btn", id="tab-btn-eda", n_clicks=0),
            html.Button("Autores", className="tab-btn", id="tab-btn-autores", n_clicks=0),
            html.Button("Bibliografía", className="tab-btn", id="tab-btn-biblio", n_clicks=0),
        ], className="tabs-inner"),
    ], className="tabs")


# ── Introducción ─────────────────────────────────────────────────────────
def intro_layout(data):
    meta = data["meta"]
    desc = data["desc_stats"][TARGET]

    kpis = html.Div([
        kpi_card("Observaciones", str(meta["n"]), f'{fmt_date(meta["fecha_min"])} — {fmt_date(meta["fecha_max"])}'),
        kpi_card("Desempleo promedio", fmt_pct(meta["mean_val"]), "Media histórica", variant="gold"),
        kpi_card("Mínimo histórico", fmt_pct(meta["min_val"]), fmt_date(meta["min_fecha"]), variant="green"),
        kpi_card("Máximo histórico", fmt_pct(meta["max_val"]), fmt_date(meta["max_fecha"]), variant="red"),
    ], className="kpis")

    var_defs = html.Div([
        html.Div([
            html.B("Tasa Global de Participación (TGP) — 13 áreas / Nacional"),
            html.P("Relación porcentual entre la población que integra la fuerza de trabajo y la población en edad de trabajar (PET). Refleja la presión de la PET sobre el mercado laboral."),
        ], className="var-def"),
        html.Div([
            html.B("Tasa de Desempleo (TD) — 13 áreas / Nacional"),
            html.P("Relación porcentual entre el número de personas desocupadas y el número de personas que integran la fuerza de trabajo (FT). Es la variable objetivo de este estudio."),
        ], className="var-def"),
        html.Div([
            html.B("Tasa de Ocupación (TO) — 13 áreas / Nacional"),
            html.P("Relación porcentual entre la población ocupada y la población en edad de trabajar (PET)."),
        ], className="var-def"),
    ], className="var-def-grid")

    return html.Div([
        html.Section([
            html.H2("Panorama general (dinámico)"),
            kpis,
        ]),
        html.Section([
            html.H2("Contexto del dataset"),
            html.P([
                "Este análisis exploratorio parte de las series históricas del mercado laboral colombiano publicadas por el ",
                html.B("Departamento Administrativo Nacional de Estadística (DANE)", style={"color": "var(--text)"}),
                " a partir de la Gran Encuesta Integrada de Hogares (GEIH), y distribuidas por el ",
                html.B("Banco de la República", style={"color": "var(--text)"}),
                " dentro de su portal de series estadísticas históricas.",
            ]),
            html.Div([
                html.Div([html.Span("Periodicidad"), html.B("Mensual")], className="meta-item"),
                html.Div([html.Span("Unidad de medida"), html.B("Porcentaje (%)")], className="meta-item"),
                html.Div([html.Span("Fuente"), html.B("DANE / Banco de la República")], className="meta-item"),
                html.Div([html.Span("Descargado"), html.B("27/02/2026")], className="meta-item"),
            ], className="meta-grid"),
            html.P("El conjunto de datos contiene 300 observaciones mensuales (25 años completos) y 6 series correspondientes a tres indicadores del mercado laboral, cada uno medido a nivel de las 13 principales áreas metropolitanas y a nivel nacional:"),
            var_defs,
        ]),
        html.Section([
            html.H2("Interpretación preliminar"),
            html.P(f"El mercado laboral colombiano es un indicador central del desempeño económico del país: refleja tanto la capacidad de la economía para generar empleo como la presión que ejerce la población en edad de trabajar sobre ese mercado. Las tres tasas que componen este dataset —participación, desempleo y ocupación— están matemáticamente relacionadas (la PET se reparte entre fuerza de trabajo e inactivos, y la fuerza de trabajo entre ocupados y desocupados), por lo que es esperable observar una fuerte correlación negativa entre desempleo y ocupación, y una relación más débil con la participación."),
            html.P(f"Los {meta['n']} meses del dataset muestran una tasa de desempleo nacional que se movió entre {fmt_pct(meta['min_val'])} ({fmt_date(meta['min_fecha'])}) y {fmt_pct(meta['max_val'])} ({fmt_date(meta['max_fecha'])}), con una media de {fmt_pct(meta['mean_val'])}. El episodio más disruptivo del periodo es, sin sorpresa, la pandemia de COVID-19: el máximo histórico se registra en plena crisis sanitaria, más de 8 puntos por encima de la media. Fuera de ese choque, la serie muestra una tendencia estructural a la baja entre 2001 y 2015, seguida de una relativa estabilización."),
            html.P("Para efectos del modelo predictivo que se construirá a futuro, este comportamiento sugiere dos cosas: (1) la serie no es estacionaria y tiene estacionalidad anual, por lo que requerirá diferenciación antes de modelarse, y (2) el periodo COVID debe tratarse explícitamente (por ejemplo, como variable dummy) en lugar de eliminarse, ya que es información real y no un error de medición."),
        ]),
    ], id="tab-intro", className="tab-panel active")


# ── EDA ──────────────────────────────────────────────────────────────────
def eda_layout(data, figs):
    desc = data["desc_stats"]
    meta = data["meta"]
    tt = data["train_test"]

    kpis = html.Div([
        kpi_card("Desempleo promedio", fmt_pct(meta["mean_val"])),
        kpi_card("Mínimo histórico", fmt_pct(meta["min_val"]), fmt_date(meta["min_fecha"]), variant="green"),
        kpi_card("Máximo histórico", fmt_pct(meta["max_val"]), fmt_date(meta["max_fecha"]), variant="red"),
        kpi_card("Observaciones", str(meta["n"]), f'{fmt_date(meta["fecha_min"])} — {fmt_date(meta["fecha_max"])}', variant="gold"),
    ], className="kpis")

    order = [TARGET] + FEATURES
    desc_rows = [
        html.Tr([html.Td(label(v)), html.Td(desc[v]["mean"]), html.Td(desc[v]["std"]), html.Td(desc[v]["min"]),
                 html.Td(desc[v]["q1"]), html.Td(desc[v]["median"]), html.Td(desc[v]["q3"]), html.Td(desc[v]["max"]),
                 html.Td(desc[v]["iqr"])])
        for v in order
    ]

    adf_rows = [
        html.Tr([
            html.Td(label(r["variable"])), html.Td(r["adf_stat"]), html.Td(r["p_value"]), html.Td(r["n_lags"]),
            html.Td(html.Span("Sí" if r["stationary"] else "No",
                               className="tag " + ("tag-si" if r["stationary"] else "tag-no"))),
        ])
        for r in data["adf"]
    ]

    return html.Div([
        html.Section([
            html.H2("1. Inspección inicial"),
            kpis,
            html.P(f'Rango: {fmt_date(meta["fecha_min"])} → {fmt_date(meta["fecha_max"])}. Sin valores faltantes ni fechas duplicadas, orden cronológico verificado.'),
            html.H3("Estadísticos descriptivos", className="chart-title"),
            html.Table([
                html.Thead(html.Tr([html.Th(c) for c in ["Variable", "Media", "DS", "Min", "Q1", "Mediana", "Q3", "Max", "IQR"]])),
                html.Tbody(desc_rows),
            ]),
        ]),
        html.Section([
            html.H2("2. Análisis univariado — variable objetivo"),
            html.P([
                "Skewness: ", html.Code(data["target_stats"]["skew"]), " Kurtosis: ", html.Code(data["target_stats"]["kurtosis"]),
                " — distribución con sesgo positivo (cola hacia valores altos de desempleo).",
            ]),
            chart_card("chart_hist_target", figs["hist_target"],
                       "La distribución del desempleo nacional tiene sesgo positivo: la mayoría de los meses se concentra entre 9% y 13%, con una cola larga hacia valores altos causada por los picos de 2020. La media queda por encima de la mediana, típico cuando hay eventos extremos ocasionales."),
            chart_card("chart_box_target", figs["box_target"],
                       "El rango intercuartílico va de 9.7% a 12.9%. Los puntos fuera de los bigotes son 5 observaciones: enero de 2002 y cuatro meses de 2020, coincidiendo con el choque del COVID-19. Se conservan por ser información real del mercado laboral."),
            html.H3("Boxplots por indicador", className="chart-title"),
            chart_card("chart_box_allvars", figs["box_allvars"],
                       "Las tasas de ocupación y participación (42–72%) tienen escalas mucho más altas que las de desempleo (7–26%), aunque todas se miden en porcentaje. La dispersión es similar entre las variables de área y las nacionales del mismo indicador."),
        ]),
        html.Section([
            html.H2("3. Bivariado y multicolinealidad"),
            chart_card("chart_corr", figs["corr"],
                       "Las correlaciones más fuertes se dan entre los pares área/nacional del mismo indicador (>0.94), lo que sugiere redundancia. El desempleo nacional correlaciona negativamente con la ocupación y débilmente con la participación."),
            chart_card("chart_vif", figs["vif"],
                       "Todas las variables predictoras superan el umbral VIF=10 (escala logarítmica), lo que confirma multicolinealidad severa. tasa_ocupacion_area es la más redundante — antes de un modelo lineal conviene eliminar duplicados o aplicar reducción de dimensionalidad."),
            chart_card("chart_scatter_feature", figs["scatter_feature"],
                       "Usa el menú desplegable para cambiar de variable. La relación con la ocupación nacional es la más clara y negativa; con las tasas de participación es más difusa, ya que entrar a la fuerza laboral no siempre implica desempleo."),
        ]),
        html.Section([
            html.H2("4. Evolución temporal"),
            chart_card("chart_evolucion", figs["evolucion"],
                       "Desempleo y ocupación nacional se mueven en direcciones opuestas casi todo el periodo. El quiebre más marcado ocurre en 2020: el desempleo se dispara mientras la ocupación cae abruptamente por las restricciones del COVID-19."),
            chart_card("chart_box_anual_des", figs["box_anual_des"],
                       "La mediana del desempleo desciende de forma sostenida entre 2001 y 2015, se estabiliza, y repunta bruscamente en 2020 antes de retomar la tendencia decreciente hasta 2025."),
            chart_card("chart_box_anual_ocu", figs["box_anual_ocu"],
                       "La ocupación nacional muestra una tendencia ascendente de largo plazo, interrumpida abruptamente en 2020, con recuperación posterior hasta niveles históricamente altos en los últimos años."),
        ]),
        html.Section([
            html.H2("5. Estacionariedad y estacionalidad"),
            html.P("Prueba ADF (H0: la serie tiene raíz unitaria / no es estacionaria) aplicada a las 6 series, no solo al target."),
            html.Table([
                html.Thead(html.Tr([html.Th(c) for c in ["Variable", "Estadístico ADF", "p-valor", "N lags", "Estacionaria"]])),
                html.Tbody(adf_rows),
            ]),
            chart_card("chart_decomp", figs["decomp"],
                       "La tendencia confirma la caída estructural del desempleo en 25 años. El componente estacional se repite cada 12 meses con amplitud estable. Los residuos se disparan en 2020, señal de que ese periodo no lo explican ni la tendencia ni la estacionalidad."),
            chart_card("chart_acf_pacf", figs["acf_pacf"],
                       "El ACF decae lentamente con picos en múltiplos de 12 — evidencia de no estacionariedad y estacionalidad anual. El PACF cae abruptamente tras los primeros rezagos, sugiriendo un componente autorregresivo de orden bajo una vez diferenciada la serie."),
        ]),
        html.Section([
            html.H2("6. Ingeniería de variables (para el modelo)"),
            html.P(["Nuevas columnas candidatas: ", html.Code("lag1"), ", ", html.Code("lag3"), ", ", html.Code("lag6"),
                    ", ", html.Code("lag12"), ", medias/desviaciones móviles a 3, 6 y 12 meses, ", html.Code("mes"),
                    " (estacionalidad) y ", html.Code("covid"), " (dummy 2020-01 a 2021-06)."]),
            chart_card("chart_lag_corr", figs["lag_corr"],
                       "El lag de 1 mes es, por mucho, el predictor más fuerte del desempleo del mes siguiente. Los rezagos estacionales (6 y 12 meses) también aportan información relevante como features del modelo."),
        ]),
        html.Section([
            html.H2("7. Split temporal train/test"),
            html.Div([
                kpi_card("Train", f'{tt["train_n"]} obs.', f'{fmt_date(tt["train_start"])} → {fmt_date(tt["train_end"])}'),
                kpi_card("Test", f'{tt["test_n"]} obs.', f'{fmt_date(tt["test_start"])} → {fmt_date(tt["test_end"])}', variant="gold"),
            ], className="kpis"),
            html.P(["Corte definido por fecha (no aleatorio) — obligatorio en series de tiempo para no filtrar información futura al entrenamiento. Dataset con features exportado en ", html.Code("MLC_featured.csv"), "."]),
        ]),
        html.Section([
            html.H2("8. Resumen de hallazgos"),
            html.Ul([
                html.Li("Dataset completo, sin nulos ni duplicados — 300 obs. mensuales, ene 2001 a dic 2025."),
                html.Li("5 outliers en el target, 4 asociados al choque COVID-19 (2020) — se conservan por ser información real."),
                html.Li("Multicolinealidad severa confirmada por VIF entre variables de área y nacional — eliminar redundantes o aplicar PCA antes de modelos lineales."),
                html.Li("Ninguna de las 6 series es estacionaria en niveles — se requiere diferenciación; la estacionalidad anual es clara en la descomposición y el ACF."),
                html.Li("Los lags 1, 3 y 12 del target son los predictores más correlacionados — candidatos naturales de feature engineering."),
                html.Li("Split temporal definido en 24 meses de test — usar este mismo corte o validación walk-forward al entrenar, nunca un split aleatorio."),
            ], className="findings"),
        ]),
    ], id="tab-eda", className="tab-panel")


# ── Autores ──────────────────────────────────────────────────────────────
AUTHORS = [
    {"name": "Andrés Parejo", "photo": "/assets/authors/parejo.png",
     "bio": "Estudiante de ciencia de datos con enfoque en educación y programación."},
    {"name": "Juan Marín", "photo": "/assets/authors/marin.png",
     "bio": "Estudiante de ciencia de datos con enfoque en estadística y ML."},
    {"name": "Santiago Hurtado", "photo": "/assets/authors/hurtado.png",
     "bio": "Estudiante de ciencia de datos con enfoque en banca, finanzas y deporte."},
]


def autores_layout():
    cards = []
    for a in AUTHORS:
        cards.append(html.Div([
            html.Div(html.Img(src=a["photo"], className="author-photo"), className="author-photo-wrap"),
            html.B(a["name"], className="author-name"),
            html.P(a["bio"], className="author-bio"),
        ], className="author-card"))
    return html.Div([
        html.Section([
            html.H2("Autores"),
            html.P("Equipo responsable del análisis exploratorio y del modelo de machine learning."),
            html.Div(cards, className="authors-grid"),
        ]),
    ], id="tab-autores", className="tab-panel")


# ── Bibliografía ─────────────────────────────────────────────────────────
def biblio_layout():
    return html.Div([
        html.Section([
            html.H2("Bibliografía"),
            html.P("Fuentes utilizadas para obtener y documentar las series del mercado laboral colombiano empleadas en este EDA."),
            html.Div([
                html.Div([
                    html.Div("Banco de la República de Colombia. (2025, 17 de julio). Series estadísticas históricas de Colombia.", className="ref-title"),
                    html.P("Portal que recopila información histórica de series económicas de Colombia, construido con base en la compilación del Banco de 1997 y complementado con fuentes como el DANE, el Ministerio de Hacienda y el DNP. Las series están organizadas en 9 categorías; la categoría \"Mercado laboral\" agrupa el salario mínimo, el auxilio de transporte y los indicadores de ocupación y desempleo usados en este estudio."),
                    html.A("https://www.banrep.gov.co/es/estadisticas-economicas/series-estadisticas-historicas-colombia",
                           href="https://www.banrep.gov.co/es/estadisticas-economicas/series-estadisticas-historicas-colombia",
                           target="_blank", rel="noopener"),
                ], className="ref-item"),
                html.Div([
                    html.Div("Banco de la República de Colombia. (s. f.). Mercado laboral — Series históricas.", className="ref-title"),
                    html.P("Fuente directa de descarga de las seis series utilizadas en este EDA: Tasa Global de Participación, Tasa de Desempleo y Tasa de Ocupación, cada una para las 13 áreas metropolitanas y el total nacional, con periodicidad mensual desde enero de 2001. Los datos originales son producidos por el DANE a partir de la GEIH."),
                    html.A("https://uba.banrep.gov.co/htmlcommons/SeriesHistoricas/mercado-laboral.html",
                           href="https://uba.banrep.gov.co/htmlcommons/SeriesHistoricas/mercado-laboral.html",
                           target="_blank", rel="noopener"),
                ], className="ref-item"),
                html.Div([
                    html.Div("Departamento Administrativo Nacional de Estadística (DANE).", className="ref-title"),
                    html.P("Entidad productora original de los indicadores del mercado laboral a partir de la Gran Encuesta Integrada de Hogares (GEIH). Sus definiciones metodológicas (TGP, TD, TO) son la base de las notas incluidas en la pestaña Introducción."),
                ], className="ref-item"),
            ], className="ref-list"),
        ]),
    ], id="tab-biblio", className="tab-panel")


def make_footer():
    return html.Footer("Universidad del Norte · Dash + Plotly · app en Python")
