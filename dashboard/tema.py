"""Identidade visual: paleta, CSS da página e layout base dos gráficos."""
from __future__ import annotations

import re

FONTE = "'Manrope', 'Segoe UI', system-ui, -apple-system, sans-serif"

COR = {
    "fundo": "#101113",
    "cartao": "#191B1E",
    "borda": "#272A2F",
    "grade": "#2A2E33",
    "destaque": "#20D6D0",
    "texto": "#F4F5F6",
    "texto2": "#8D939B",
    "neutro": "#4A5058",      # barras de volume (elegíveis, solicitados, analisadas)
    "ok": "#3DDC97",
    "atencao": "#F5C451",
    "critico": "#FF5C6C",
}
# Categorias sem significado de alerta (canais, resultados): tons claros que
# aceitam texto escuro por cima.
PALETA = ["#20D6D0", "#8E9BFF", "#9AA3AF", "#E1E4E8"]
COR_STATUS = {
    "ok": COR["ok"],
    "atencao": COR["atencao"],
    "critico": COR["critico"],
    "sem_meta": COR["texto2"],
}
# Matriz de riscos: versões amenizadas dos semáforos para servir de fundo de célula.
MATRIZ = {"baixo": "#1D5A43", "medio": "#7A6420", "alto": "#8C2F3A"}


# --------------------------------------------------------------------------- Plotly
EIXO_X = dict(
    showgrid=False, zeroline=False, linecolor=COR["grade"], ticks="", automargin=True,
    tickfont=dict(color=COR["texto2"], size=11), fixedrange=True,
)
EIXO_Y = dict(
    showgrid=True, gridcolor=COR["grade"], zeroline=False, showline=False, ticks="", automargin=True,
    tickfont=dict(color=COR["texto2"], size=11), fixedrange=True,
)


def layout(altura: int = 320, legenda: bool = True, **extra) -> dict:
    base = dict(
        height=altura,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONTE, color=COR["texto2"], size=12),
        margin=dict(l=4, r=4, t=40 if legenda else 10, b=6),
        separators=",.",
        showlegend=legenda,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(color=COR["texto2"], size=11), bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor="#0C0D0F", bordercolor=COR["borda"],
            font=dict(family=FONTE, color=COR["texto"], size=12),
        ),
    )
    base.update(extra)
    return base


# --------------------------------------------------------------------------- CSS
_IMPORT_FONTE = (
    "@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');"
)

_CSS = """
.stApp, .stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stMarkdownContainer"] * { font-family: var(--fonte); }
.stApp { background: var(--fundo); color: var(--texto); }
.stApp [data-testid="stHeader"] { background: transparent; }
.stApp #MainMenu, .stApp footer, .stApp [data-testid="stDecoration"],
.stApp [data-testid="stSidebar"], .stApp [data-testid="stSidebarCollapsedControl"],
.stApp [data-testid="collapsedControl"] { display: none; }
.stApp [data-testid="stMainBlockContainer"], .stApp .block-container { max-width: 1480px; padding: 2.4rem 2.6rem 4rem; }
.stApp [data-testid="stVerticalBlock"], .stApp [data-testid="stHorizontalBlock"] { gap: 1.25rem; }
.stApp [data-testid="stMarkdownContainer"] p { margin: 0; }

/* cartões de gráfico (st.container com key="card_...") */
.stApp [class*="st-key-card_"] { gap: .3rem; background: var(--cartao); border: 1px solid var(--borda); border-radius: 14px; padding: 1.3rem 1.3rem .9rem; }
.stApp [data-testid="stPlotlyChart"] { margin-top: .2rem; overflow: hidden; }
.cd-titulo { font-size: 1.02rem; font-weight: 700; letter-spacing: -.01em; color: var(--texto); }
.cd-sub { font-size: .8rem; color: var(--texto2); line-height: 1.3; margin-top: .2rem; min-height: 2.6em; }

/* cabeçalho */
.cd-header { display: flex; justify-content: space-between; align-items: flex-end; gap: 1.5rem; flex-wrap: wrap; }
.cd-sistema { display: flex; align-items: center; gap: .55rem; font-size: .9rem; font-weight: 700; color: var(--destaque); }
.cd-marca { width: .72rem; height: .72rem; border-radius: 3px; background: var(--destaque); }
.cd-h1 { font-size: clamp(1.9rem, 3vw, 2.7rem); font-weight: 800; letter-spacing: -.03em; line-height: 1.1; margin: .55rem 0 .45rem; color: var(--texto); }
.cd-lead { font-size: .95rem; color: var(--texto2); }
.cd-resumo { display: flex; gap: .6rem; flex-wrap: wrap; }
.cd-chip { display: inline-flex; align-items: center; gap: .5rem; padding: .45rem .85rem; border: 1px solid var(--borda); background: var(--cartao); border-radius: 10px; font-size: .82rem; color: var(--texto2); }
.cd-chip b { color: var(--texto); font-size: 1rem; font-variant-numeric: tabular-nums; }
.cd-chip i { width: .5rem; height: .5rem; border-radius: 50%; }

/* seções */
.cd-secao { margin: 1.5rem 0 .1rem; }
.cd-secao-t { font-size: 1.2rem; font-weight: 700; letter-spacing: -.01em; color: var(--texto); }
.cd-secao-s { font-size: .85rem; color: var(--texto2); margin-top: .15rem; }

/* cartões de indicador */
.cd-grade { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.25rem; }
.cd-kpi { background: var(--cartao); border: 1px solid var(--borda); border-radius: 14px; padding: 1.2rem 1.3rem 1.15rem; display: flex; flex-direction: column; }
.cd-kpi--critico { border-color: rgba(255, 92, 108, .45); }
.cd-kpi-topo { display: flex; justify-content: space-between; align-items: flex-start; gap: .75rem; flex-wrap: wrap; }
.cd-kpi-titulo { font-size: 1.05rem; font-weight: 700; color: var(--texto); }
.cd-kpi-desc { font-size: .8rem; color: var(--texto2); line-height: 1.3; margin-top: .2rem; }
.cd-kpi-valor { font-size: 2.4rem; font-weight: 800; letter-spacing: -.03em; line-height: 1.1; margin-top: 1rem; color: var(--texto); font-variant-numeric: tabular-nums; }
.cd-kpi-valor small { font-size: 1rem; font-weight: 600; letter-spacing: 0; color: var(--texto2); margin-left: .4rem; }
.cd-kpi-meta { font-size: .82rem; color: var(--texto2); margin-top: .35rem; }
.cd-pill { display: inline-flex; align-items: center; gap: .45rem; padding: .22rem .65rem; border-radius: 999px; font-size: .75rem; font-weight: 600; white-space: nowrap; }
.cd-pill i { width: .45rem; height: .45rem; border-radius: 50%; background: currentColor; }
.cd-ok { color: var(--ok); background: rgba(61, 220, 151, .12); }
.cd-atencao { color: var(--atencao); background: rgba(245, 196, 81, .12); }
.cd-critico { color: var(--critico); background: rgba(255, 92, 108, .12); }
.cd-sem_meta { color: var(--texto2); background: rgba(141, 147, 155, .12); }

/* notas sobre os dados */
.stApp [data-testid="stExpander"] details { background: var(--cartao); border: 1px solid var(--borda); border-radius: 14px; }
.stApp [data-testid="stExpander"] summary { color: var(--texto2); }
.stApp [data-testid="stExpander"] li { color: var(--texto2); font-size: .85rem; margin-bottom: .3rem; }

/* responsividade */
@media (max-width: 1100px) {
  .stApp [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
  .stApp [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
  .stApp [data-testid="stHorizontalBlock"] > [data-testid="column"] { flex: 1 1 420px !important; min-width: min(100%, 420px) !important; }
}
@media (max-width: 820px) {
  .cd-grade { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
  .stApp [data-testid="stMainBlockContainer"], .stApp .block-container { padding: 1.6rem 1.2rem 3rem; }
}
@media (max-width: 520px) {
  .cd-grade { grid-template-columns: minmax(0, 1fr); }
  .cd-kpi-valor { font-size: 2.1rem; }
}
"""


def css() -> str:
    variaveis = (
        ":root {"
        f"--fonte: {FONTE};"
        f"--fundo: {COR['fundo']}; --cartao: {COR['cartao']}; --borda: {COR['borda']};"
        f"--destaque: {COR['destaque']}; --texto: {COR['texto']}; --texto2: {COR['texto2']};"
        f"--ok: {COR['ok']}; --atencao: {COR['atencao']}; --critico: {COR['critico']};"
        "}"
    )
    # Minifica: linhas em branco dentro do HTML quebram o parser de markdown do Streamlit.
    return re.sub(r"\s+", " ", _IMPORT_FONTE + variaveis + _CSS).strip()
