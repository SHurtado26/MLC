"""Construcción de todas las figuras Plotly de la pestaña EDA, en Python puro."""
import plotly.graph_objects as go

import theme as t
from data_loader import FEATURES, TARGET, label


def fig_hist_target(data):
    df = data["df"]
    ds = data["desc_stats"][TARGET]
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df[TARGET], nbinsx=28, name="Frecuencia",
        marker=dict(color=t.NAVY_A, line=dict(color=t.NAVY, width=1)),
    ))
    layout = t.base_layout("Distribución — Desempleo Nacional")
    layout["shapes"] = [
        dict(type="line", x0=ds["mean"], x1=ds["mean"], y0=0, y1=1, yref="paper",
             line=dict(color=t.RED, dash="dash", width=2)),
        dict(type="line", x0=ds["median"], x1=ds["median"], y0=0, y1=1, yref="paper",
             line=dict(color=t.GOLD, dash="dash", width=2)),
    ]
    layout["annotations"] = [
        dict(x=ds["mean"], y=1.1, yref="paper", text="Media", showarrow=False, font=dict(color=t.RED, size=10)),
        dict(x=ds["median"], y=1.18, yref="paper", text="Mediana", showarrow=False, font=dict(color=t.GOLD, size=10)),
    ]
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


def fig_box_target(data):
    df = data["df"]
    fig = go.Figure(go.Box(
        y=df[TARGET], name=label(TARGET), boxpoints="outliers",
        marker=dict(color=t.RED, size=4), line=dict(color=t.NAVY, width=2), fillcolor=t.NAVY_A,
    ))
    layout = t.base_layout("Boxplot — Desempleo Nacional")
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


def fig_box_allvars(data):
    df = data["df"]
    variables = [TARGET] + FEATURES
    palette = [t.RED, t.NAVY, t.NAVY, t.RED, t.TEAL, t.TEAL]
    fig = go.Figure()
    for v, c in zip(variables, palette):
        fig.add_trace(go.Box(y=df[v], name=label(v), marker=dict(color=c, size=3),
                              line=dict(color=c, width=1.5), fillcolor=t.rgba(c, 0.22)))
    layout = t.base_layout("Distribución por indicador", height=420)
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


def fig_corr(data):
    cm = data["corr"]
    labels = [label(v) for v in cm.columns]
    fig = go.Figure(go.Heatmap(
        z=cm.values, x=labels, y=labels, zmin=-1, zmax=1,
        colorscale=[[0, t.RED], [0.5, t.CARD_2], [1, t.NAVY]],
        text=[[f"{v:.2f}" for v in row] for row in cm.values], texttemplate="%{text}",
        textfont=dict(color=t.TEXT, size=10.5), hoverongaps=False,
        colorbar=dict(tickfont=dict(color=t.SUB)),
    ))
    layout = t.base_layout("Matriz de correlación", height=420)
    layout["margin"]["l"] = 150
    layout["xaxis"]["tickangle"] = -35
    fig.update_layout(**layout)
    return fig


def fig_vif(data):
    rows = data["vif"]
    fig = go.Figure(go.Bar(
        x=[r["vif"] for r in rows], y=[label(r["variable"]) for r in rows], orientation="h",
        marker=dict(color=[t.RED if r["vif"] > 10 else t.GREEN for r in rows]),
        text=[r["vif"] for r in rows], texttemplate="%{text}", textposition="outside",
        textfont=dict(color=t.SUB),
    ))
    layout = t.base_layout("VIF — Multicolinealidad (escala log)")
    layout["xaxis"]["type"] = "log"
    layout["xaxis"]["title"] = "VIF"
    layout["margin"]["l"] = 190
    layout["shapes"] = [dict(type="line", x0=10, x1=10, y0=0, y1=1, yref="paper",
                              line=dict(color=t.GOLD, dash="dot", width=2))]
    import math
    layout["annotations"] = [dict(x=math.log10(10), y=1.08, yref="paper", text="Umbral VIF = 10",
                                   showarrow=False, font=dict(color=t.GOLD, size=10))]
    fig.update_layout(**layout)
    return fig


def fig_scatter_feature(data):
    df = data["df"]
    fig = go.Figure()
    for i, f in enumerate(FEATURES):
        fig.add_trace(go.Scatter(
            x=df[f], y=df[TARGET], mode="markers", name=label(f), visible=(i == 0),
            marker=dict(color=t.NAVY, opacity=0.6, size=6),
        ))
    buttons = []
    for i, f in enumerate(FEATURES):
        vis = [j == i for j in range(len(FEATURES))]
        buttons.append(dict(
            method="update",
            args=[{"visible": vis}, {"title": f"{label(f)} vs {label(TARGET)}", "xaxis.title.text": label(f)}],
            label=label(f),
        ))
    layout = t.base_layout(f"{label(FEATURES[0])} vs {label(TARGET)}")
    layout["xaxis"]["title"] = dict(text=label(FEATURES[0]), font=dict(color=t.SUB))
    layout["yaxis"]["title"] = dict(text=label(TARGET), font=dict(color=t.SUB))
    layout["showlegend"] = False
    layout["updatemenus"] = [dict(
        buttons=buttons, direction="down", x=1, xanchor="right", y=1.24, yanchor="top",
        bgcolor=t.CARD_2, bordercolor=t.BORDER, font=dict(color=t.TEXT, size=11),
    )]
    fig.update_layout(**layout)
    return fig


def fig_evolucion(data):
    df = data["df"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["fecha"], y=df[TARGET], mode="lines", name="Desempleo",
                              line=dict(color=t.RED, width=2)))
    fig.add_trace(go.Scatter(x=df["fecha"], y=df["tasa_ocupacion_nacional"], mode="lines", name="Ocupación",
                              line=dict(color=t.NAVY, width=2)))
    layout = t.base_layout("Evolución temporal — Desempleo vs Ocupación Nacional")
    layout["shapes"] = [dict(type="rect", x0="2020-01-01", x1="2021-06-01", y0=0, y1=1, yref="paper",
                              fillcolor=t.SUB, opacity=0.12, line=dict(width=0))]
    layout["annotations"] = [dict(x="2020-04-01", y=0.95, yref="paper", text="COVID-19",
                                   showarrow=False, font=dict(color=t.SUB, size=11))]
    fig.update_layout(**layout)
    return fig


def fig_box_anual(data, variable, color, title):
    df = data["df"]
    fig = go.Figure(go.Box(
        x=df["anio"].astype(str), y=df[variable], marker=dict(color=color, size=3),
        line=dict(color=color, width=1.5), fillcolor=t.rgba(color, 0.22),
    ))
    layout = t.base_layout(title)
    layout["showlegend"] = False
    layout["xaxis"]["type"] = "category"
    fig.update_layout(**layout)
    return fig


def fig_decomp(data):
    dec = data["decomposition"]
    fecha = dec.observed.index
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fecha, y=dec.observed, mode="lines", name="Observado",
                              line=dict(color=t.NAVY, width=1.6), xaxis="x", yaxis="y"))
    fig.add_trace(go.Scatter(x=fecha, y=dec.trend, mode="lines", name="Tendencia",
                              line=dict(color=t.GOLD, width=1.6), xaxis="x2", yaxis="y2"))
    fig.add_trace(go.Scatter(x=fecha, y=dec.seasonal, mode="lines", name="Estacional",
                              line=dict(color=t.TEAL, width=1.2), xaxis="x3", yaxis="y3"))
    fig.add_trace(go.Scatter(x=fecha, y=dec.resid, mode="lines", name="Residuo",
                              line=dict(color=t.RED, width=1.2), xaxis="x4", yaxis="y4"))
    layout = t.base_layout("Descomposición multiplicativa — Desempleo Nacional", height=680)
    layout["grid"] = dict(rows=4, columns=1, pattern="independent", roworder="top to bottom")
    layout["showlegend"] = False
    for s in ["", "2", "3", "4"]:
        layout[f"xaxis{s}"] = dict(gridcolor=t.BORDER, tickfont=dict(color=t.SUB, size=9))
        layout[f"yaxis{s}"] = dict(gridcolor=t.BORDER, tickfont=dict(color=t.SUB, size=9))
    layout["annotations"] = [
        dict(text="Observado", x=0, xref="paper", xanchor="left", y=1.0, yref="paper", showarrow=False, font=dict(color=t.NAVY, size=10.5)),
        dict(text="Tendencia", x=0, xref="paper", xanchor="left", y=0.72, yref="paper", showarrow=False, font=dict(color=t.GOLD, size=10.5)),
        dict(text="Estacional", x=0, xref="paper", xanchor="left", y=0.46, yref="paper", showarrow=False, font=dict(color=t.TEAL, size=10.5)),
        dict(text="Residuo", x=0, xref="paper", xanchor="left", y=0.20, yref="paper", showarrow=False, font=dict(color=t.RED, size=10.5)),
    ]
    fig.update_layout(**layout)
    return fig


def fig_acf_pacf(data):
    import math
    n = data["meta"]["n"]
    band = 1.96 / math.sqrt(n)
    acf_d, pacf_d = data["acf"], data["pacf"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=acf_d["lags"], y=acf_d["values"], name="ACF", marker=dict(color=t.NAVY), xaxis="x", yaxis="y"))
    fig.add_trace(go.Bar(x=pacf_d["lags"], y=pacf_d["values"], name="PACF", marker=dict(color=t.TEAL), xaxis="x2", yaxis="y2"))
    layout = t.base_layout("Serie diferenciada — ACF y PACF (36 rezagos)", height=480)
    layout["grid"] = dict(rows=2, columns=1, pattern="independent")
    layout["showlegend"] = False
    for s in ["", "2"]:
        layout[f"xaxis{s}"] = dict(gridcolor=t.BORDER, tickfont=dict(color=t.SUB, size=9))
        layout[f"yaxis{s}"] = dict(gridcolor=t.BORDER, tickfont=dict(color=t.SUB, size=9))
    nlag = len(acf_d["lags"]) - 1
    layout["shapes"] = []
    for xref, yref in [("x", "y"), ("x2", "y2")]:
        layout["shapes"].append(dict(type="line", x0=0, x1=nlag, y0=band, y1=band, xref=xref, yref=yref,
                                      line=dict(color=t.SUB, dash="dot", width=1)))
        layout["shapes"].append(dict(type="line", x0=0, x1=nlag, y0=-band, y1=-band, xref=xref, yref=yref,
                                      line=dict(color=t.SUB, dash="dot", width=1)))
    layout["annotations"] = [
        dict(text="ACF", x=0, xref="paper", xanchor="left", y=1.0, yref="paper", showarrow=False, font=dict(color=t.NAVY, size=10.5)),
        dict(text="PACF", x=0, xref="paper", xanchor="left", y=0.42, yref="paper", showarrow=False, font=dict(color=t.TEAL, size=10.5)),
    ]
    fig.update_layout(**layout)
    return fig


def fig_lag_corr(data):
    rows = data["lag_corr"]
    fig = go.Figure(go.Bar(
        x=[f"lag {r['lag']}" for r in rows], y=[r["corr"] for r in rows], marker=dict(color=t.GOLD),
        text=[r["corr"] for r in rows], textposition="outside", textfont=dict(color=t.SUB),
    ))
    layout = t.base_layout("Correlación del target con sus rezagos")
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig
