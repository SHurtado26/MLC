"""
Paleta institucional: azul marino (banca/confianza) + dorado apagado
(acento, referencia al sello del Banco de la República) + rojo/verde
pastel solo con función semántica en los gráficos (sube/baja).
Sin colores decorativos adicionales — nada de "carnaval de colores".
"""

BG = "#0a0e17"
CARD = "#131a29"
CARD_2 = "#182236"
BORDER = "#232d40"
TEXT = "#e9ecf3"
SUB = "#98a2ba"

NAVY = "#6f9bd1"       # azul institucional (observado / serie principal)
GOLD = "#cda65e"       # dorado apagado (acento, tendencia, umbrales)
TEAL = "#5fa89c"       # verde azulado neutro (estacionalidad — misma familia fría)
RED = "#e0a3a3"        # semántico: sube / negativo (desempleo, residuo)
GREEN = "#a3d9b8"       # semántico: baja / positivo (ocupación)

def rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

NAVY_A = rgba(NAVY, 0.25)
GOLD_A = rgba(GOLD, 0.25)
TEAL_A = rgba(TEAL, 0.25)
RED_A = rgba(RED, 0.25)
GREEN_A = rgba(GREEN, 0.25)

FONT_FAMILY = "'Segoe UI', Inter, Arial, sans-serif"


def base_layout(title="", height=360):
    return dict(
        title=dict(text=title, font=dict(color=TEXT, size=13.5, family=FONT_FAMILY)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=SUB, family=FONT_FAMILY, size=11),
        xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, tickfont=dict(color=SUB)),
        yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, tickfont=dict(color=SUB)),
        legend=dict(font=dict(color=SUB), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=46, r=20, b=40, l=50),
        height=height,
    )


PLOTLY_CONFIG = {"responsive": True, "displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d"]}
