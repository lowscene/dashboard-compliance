"""Construção dos gráficos (Plotly). Cada função recebe os dados e devolve uma Figure."""
from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import formatos as f
from . import tema
from .dados import Dados
from .indicadores import Resultado, avaliar

COR = tema.COR
TEMPO = dict(hovermode="x unified")


def _meta(d: Dados, chave: str) -> float:
    return d.kpis[chave][1]


def _linha_meta(cor: str = COR["texto2"]) -> dict:
    return dict(color=cor, width=1.5, dash="dash")


# --------------------------------------------------------------------------- 1
def treinamentos(d: Dados) -> go.Figure:
    """Concluídos x elegíveis por mês, com ITR e meta de ITR."""
    m = d.mensal
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=m["Mês"], y=m["Treinamentos Elegíveis"], name="Elegíveis",
                marker_color=COR["neutro"], secondary_y=False)
    fig.add_bar(x=m["Mês"], y=m["Treinamentos Concluídos"], name="Concluídos",
                marker_color=COR["destaque"], secondary_y=False)
    fig.add_scatter(x=m["Mês"], y=m["ITR %"], name="ITR", mode="lines+markers",
                    line=dict(color=COR["texto"], width=2), marker=dict(size=6),
                    secondary_y=True)
    fig.add_scatter(x=m["Mês"], y=m["Meta ITR %"], name="Meta de ITR", mode="lines",
                    line=_linha_meta(COR["atencao"]), secondary_y=True)
    fig.update_layout(**tema.layout(barmode="group", bargap=0.28, bargroupgap=0.06, **TEMPO))
    fig.update_xaxes(**tema.EIXO_X)
    fig.update_yaxes(**tema.EIXO_Y, secondary_y=False)
    fig.update_yaxes(showgrid=False, zeroline=False, ticks="", fixedrange=True, automargin=True,
                     range=[0.6, 1.02], tickformat=".0%", hoverformat=".1%",
                     tickfont=dict(color=COR["texto2"], size=11), secondary_y=True)
    return fig


# --------------------------------------------------------------------------- 2
def itens_status(resultados: list[Resultado]) -> list[Resultado]:
    """Linhas do gráfico de status; a ordem define o `point_index` de um clique."""
    return [r for r in resultados if r.atingimento == r.atingimento]  # descarta NaN


def status_indicadores(resultados: list[Resultado]) -> go.Figure:
    """Atingimento da meta de cada indicador (100% = meta cumprida).

    Para indicadores em que menor é melhor (TMI, Benford, waivers, risco),
    o atingimento é meta ÷ valor, de modo que 100% ou mais significa dentro da meta.
    """
    itens = itens_status(resultados)
    fig = go.Figure(go.Bar(
        x=[r.atingimento for r in itens],
        y=[r.indicador.rotulo for r in itens],
        orientation="h",
        marker_color=[tema.COR_STATUS[r.status] for r in itens],
        text=[f"{r.valor_fmt} (meta {r.meta_fmt})" for r in itens],
        textposition="outside", cliponaxis=False,
        textfont=dict(color=COR["texto"], size=11),
        customdata=[f"{f.pct(r.atingimento, 0)} da meta" for r in itens],
        hovertemplate="%{y}: %{customdata}<extra></extra>",
        name="Indicadores", showlegend=False,
        selected=dict(marker=dict(opacity=1)),
        unselected=dict(marker=dict(opacity=0.35)),
    ))
    fig.add_vline(x=1, line=dict(color=COR["texto"], width=1.2, dash="dash"), opacity=0.55)
    # entrada de legenda para a linha de meta
    fig.add_scatter(x=[None], y=[None], mode="lines", name="Meta (100%)",
                    line=dict(color=COR["texto"], width=1.2, dash="dash"))
    fig.update_layout(**tema.layout(bargap=0.38))
    fig.update_xaxes(**tema.EIXO_Y, range=[0, 1.75], tickvals=[0, 0.5, 1],
                     ticktext=["0%", "50%", "100%"])
    fig.update_yaxes(**{**tema.EIXO_X, "tickfont": dict(color=COR["texto"], size=12)},
                     autorange="reversed")
    return fig


# --------------------------------------------------------------------------- 3
def tmi(d: Dados) -> go.Figure:
    """TMI por mês com a referência (SLA) de 30 dias."""
    m = d.mensal
    sla = m["SLA TMI"]
    cores = [COR["destaque"] if v <= s else COR["atencao"] for v, s in zip(m["TMI"], sla)]
    fig = go.Figure()
    fig.add_scatter(x=m["Mês"], y=m["TMI"], name="TMI", mode="lines+markers",
                    line=dict(color=COR["destaque"], width=2.5),
                    marker=dict(color=cores, size=9, line=dict(color=COR["cartao"], width=2)))
    fig.add_scatter(x=m["Mês"], y=sla, name=f"Referência de {f.curto(sla.iloc[-1])} dias",
                    mode="lines", line=_linha_meta(COR["texto"]))
    piso = min(m["TMI"].min(), sla.min()) - 3
    teto = max(m["TMI"].max(), sla.max()) + 3
    fig.update_layout(**tema.layout(**TEMPO))
    fig.update_xaxes(**tema.EIXO_X)
    fig.update_yaxes(**tema.EIXO_Y, range=[piso, teto], ticksuffix=" d", hoverformat=".1f")
    return fig


# --------------------------------------------------------------------------- 4
def origem_denuncias(d: Dados) -> go.Figure:
    c = d.canais
    total = c["Quantidade"].sum()
    fig = go.Figure(go.Pie(
        labels=c["Canal"], values=c["Quantidade"], hole=0.64, sort=False,
        marker=dict(colors=tema.PALETA[: len(c)], line=dict(color=COR["cartao"], width=3)),
        texttemplate="%{percent:.0%}", textfont=dict(color="#101113", size=12),
        insidetextorientation="horizontal",
        hovertemplate="%{label}: %{value} relatos (%{percent})<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>{f.num(total)}</b><br><span style='font-size:12px'>relatos</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(size=28, color=COR["texto"]),
    )
    fig.update_layout(**tema.layout(
        margin=dict(l=4, r=4, t=10, b=40),
        legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5,
                    font=dict(color=COR["texto2"], size=11), bgcolor="rgba(0,0,0,0)"),
    ))
    return fig


# --------------------------------------------------------------------------- 5
def resultados_investigacoes(d: Dados) -> go.Figure:
    t = d.trimestres
    series = [("Procedente", tema.PALETA[0]), ("Improcedente", tema.PALETA[2]),
              ("Inconclusivo", tema.PALETA[1]), ("Em Aberto", tema.PALETA[3])]
    fig = go.Figure()
    for coluna, cor in series:
        fig.add_bar(x=t["Trimestre"], y=t[coluna], name=coluna.replace("Em Aberto", "Em aberto"),
                    marker_color=cor, texttemplate="%{y}", textposition="inside",
                    textfont=dict(color="#101113", size=11),
                    hovertemplate="%{x}: %{y} casos<extra>" + coluna + "</extra>")
    total = t[[c for c, _ in series]].sum(axis=1)
    fig.add_scatter(x=t["Trimestre"], y=total, mode="text", text=[f.num(v) for v in total],
                    textposition="top center", textfont=dict(color=COR["texto"], size=12),
                    showlegend=False, hoverinfo="skip")
    fig.update_layout(**tema.layout(barmode="stack", bargap=0.35))
    fig.update_xaxes(**tema.EIXO_X)
    fig.update_yaxes(**tema.EIXO_Y, range=[0, total.max() * 1.15])
    return fig


# --------------------------------------------------------------------------- 6
def _banda(score: float) -> int:
    """Faixa de severidade de probabilidade × impacto numa escala 1-4 (máx. 16)."""
    if score <= 4:
        return 0
    return 1 if score <= 9 else 2


def matriz_riscos(d: Dados) -> go.Figure:
    r = d.riscos
    niveis = [1, 2, 3, 4]
    z = [[_banda(p * i) for i in niveis] for p in niveis]   # linhas = probabilidade
    verde, amarelo, vermelho = (tema.MATRIZ[k] for k in ("baixo", "medio", "alto"))
    escala = [[0, verde], [0.33, verde], [0.34, amarelo], [0.66, amarelo], [0.67, vermelho], [1, vermelho]]

    fig = go.Figure(go.Heatmap(
        x=niveis, y=niveis, z=z, zmin=0, zmax=2, colorscale=escala, showscale=False,
        xgap=4, ygap=4, hoverinfo="skip",
    ))

    # Riscos que caem na mesma célula são listados juntos.
    celulas: dict[tuple[int, int], list[str]] = {}
    detalhes: dict[tuple[int, int], list[str]] = {}
    for _, linha in r.iterrows():
        chave = (int(linha["Probabilidade (1-4)"]), int(linha["Impacto (1-4)"]))
        celulas.setdefault(chave, []).append(linha["ID"])
        detalhes.setdefault(chave, []).append(
            f"<b>{linha['ID']}</b> {linha['Descrição do Risco']}"
            f"<br>Risco residual: {f.num(linha['Risco Residual'], 1)}"
        )
    fig.add_scatter(
        x=[k[1] for k in celulas], y=[k[0] for k in celulas], mode="text",
        text=["<br>".join(v) for v in celulas.values()],
        textfont=dict(color=COR["texto"], size=14, family=tema.FONTE),
        customdata=["<br>".join(v) for v in detalhes.values()],
        hovertemplate="%{customdata}<extra></extra>", showlegend=False,
    )
    for nome, cor in (("Baixo", verde), ("Médio", amarelo), ("Alto", vermelho)):
        fig.add_scatter(x=[None], y=[None], mode="markers", name=nome,
                        marker=dict(symbol="square", size=10, color=cor))

    fig.update_layout(**tema.layout(margin=dict(l=4, r=4, t=40, b=6)))
    fig.update_xaxes(showgrid=False, zeroline=False, ticks="", fixedrange=True, automargin=True,
                     tickvals=niveis, range=[0.5, 4.5], title=dict(text="Impacto", standoff=8),
                     tickfont=dict(color=COR["texto"], size=12))
    fig.update_yaxes(showgrid=False, zeroline=False, ticks="", fixedrange=True, automargin=True,
                     tickvals=niveis, range=[0.5, 4.5], title=dict(text="Probabilidade", standoff=8),
                     tickfont=dict(color=COR["texto"], size=12))
    return fig


# --------------------------------------------------------------------------- 7
def due_diligence(d: Dados) -> go.Figure:
    forn = d.fornecedores
    meta = _meta(d, "DDI %")
    fig = go.Figure(go.Bar(
        x=forn["DDI %"], y=forn["Categoria Fornecedor"], orientation="h",
        marker_color=COR["destaque"], text=[f.pct(v, 0) for v in forn["DDI %"]],
        textposition="outside", cliponaxis=False, textfont=dict(color=COR["texto"], size=12),
        hovertemplate="%{y}: %{x:.1%}<extra></extra>", showlegend=False,
    ))
    if meta == meta:   # não é NaN
        fig.add_vline(x=meta, line=dict(color=COR["texto"], width=1.2, dash="dash"), opacity=0.55)
        fig.add_scatter(x=[None], y=[None], mode="lines", name=f"Meta do indicador ({f.pct_curto(meta)})",
                        line=dict(color=COR["texto"], width=1.2, dash="dash"))
    fig.update_layout(**tema.layout(bargap=0.4, showlegend=True))
    fig.update_xaxes(**tema.EIXO_Y, range=[0, 1.12], tickformat=".0%", tickvals=[0, 0.25, 0.5, 0.75, 1])
    fig.update_yaxes(**{**tema.EIXO_X, "tickfont": dict(color=COR["texto"], size=12)},
                     autorange="reversed")
    return fig


# --------------------------------------------------------------------------- 8
def cultura_etica(d: Dados) -> go.Figure:
    e = d.eci
    meta = _meta(d, "Score ECI")
    nomes = list(e["Dimensão Organizacional"])
    valores = list(e["Score ECI"])
    teto = max([meta] + valores) if meta == meta else max(valores)
    teto = float(int(teto) if teto == int(teto) else int(teto) + 1)

    fig = go.Figure()
    if meta == meta:
        fig.add_trace(go.Scatterpolar(
            r=[meta] * (len(nomes) + 1), theta=nomes + nomes[:1], mode="lines",
            name=f"Meta ({f.curto(meta)})", line=_linha_meta(), hoverinfo="skip",
        ))
    fig.add_trace(go.Scatterpolar(
        r=valores + valores[:1], theta=nomes + nomes[:1], mode="lines+markers",
        name="Score atual", fill="toself", fillcolor="rgba(32, 214, 208, 0.18)",
        line=dict(color=COR["destaque"], width=2.5), marker=dict(size=6, color=COR["destaque"]),
        hovertemplate="%{theta}: %{r:.1f}<extra></extra>",
    ))
    fig.update_layout(**tema.layout(
        margin=dict(l=56, r=56, t=40, b=14),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, teto], tickvals=list(range(1, int(teto) + 1)),
                            gridcolor=COR["grade"], linecolor=COR["grade"], angle=90,
                            tickfont=dict(color=COR["texto2"], size=10)),
            angularaxis=dict(gridcolor=COR["grade"], linecolor=COR["grade"],
                             tickfont=dict(color=COR["texto"], size=11)),
        ),
    ))
    return fig


# --------------------------------------------------------------------------- 9
def waivers(d: Dados) -> go.Figure:
    m = d.mensal
    meta = _meta(d, "Taxa de Waivers")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=m["Mês"], y=m["Waivers Solicitados"], name="Solicitados",
                marker_color=COR["neutro"], secondary_y=False)
    fig.add_bar(x=m["Mês"], y=m["Waivers Aprovados"], name="Aprovados",
                marker_color=COR["destaque"], secondary_y=False)
    fig.add_scatter(x=m["Mês"], y=m["Taxa Waivers"], name="Taxa de waivers", mode="lines+markers",
                    line=dict(color=COR["texto"], width=2), marker=dict(size=6), secondary_y=True)
    topo = m["Taxa Waivers"].max()
    if meta == meta:
        fig.add_scatter(x=m["Mês"], y=[meta] * len(m), name=f"Meta ({f.pct_curto(meta)})", mode="lines",
                        line=_linha_meta(COR["atencao"]), secondary_y=True)
        topo = max(topo, meta)
    fig.update_layout(**tema.layout(barmode="group", bargap=0.28, bargroupgap=0.06, **TEMPO))
    fig.update_xaxes(**tema.EIXO_X)
    fig.update_yaxes(**tema.EIXO_Y, secondary_y=False)
    fig.update_yaxes(showgrid=False, zeroline=False, ticks="", fixedrange=True, automargin=True,
                     range=[0, topo * 1.4], tickformat=".0%", hoverformat=".1%",
                     tickfont=dict(color=COR["texto2"], size=11), secondary_y=True)
    return fig


# --------------------------------------------------------------------------- 10
def benford(d: Dados) -> go.Figure:
    m = d.mensal
    meta = _meta(d, "Desvio Benford %")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=m["Mês"], y=m["Transações Analisadas"], name="Transações analisadas",
                marker_color=COR["neutro"], secondary_y=False)
    cores = [COR["atencao"] if (meta == meta and v > meta) else COR["destaque"]
             for v in m["Desvio Benford %"]]
    fig.add_scatter(x=m["Mês"], y=m["Desvio Benford %"], name="Fora do padrão (%)",
                    mode="lines+markers", line=dict(color=COR["destaque"], width=2.5),
                    marker=dict(size=8, color=cores, line=dict(color=COR["cartao"], width=2)),
                    secondary_y=True)
    topo = m["Desvio Benford %"].max()
    if meta == meta:
        fig.add_scatter(x=m["Mês"], y=[meta] * len(m), name=f"Meta ({f.pct_curto(meta)})", mode="lines",
                        line=_linha_meta(COR["texto"]), secondary_y=True)
        topo = max(topo, meta)
    fig.update_layout(**tema.layout(bargap=0.35, **TEMPO))
    fig.update_xaxes(**tema.EIXO_X)
    fig.update_yaxes(**tema.EIXO_Y, secondary_y=False, tickformat=",", hoverformat=",")
    fig.update_yaxes(showgrid=False, zeroline=False, ticks="", fixedrange=True, automargin=True,
                     range=[0, topo * 1.45], tickformat=".0%", hoverformat=".2%",
                     tickfont=dict(color=COR["texto2"], size=11), secondary_y=True)
    return fig


# --------------------------------------------------------------------------- indicador x meta
# Série mensal (coluna do valor, coluna da meta ou None para usar a meta da tabela KPI).
SERIES_MENSAIS = {
    "ITR %": ("ITR %", "Meta ITR %"),
    "TMI (Dias)": ("TMI", "SLA TMI"),
    "DDI %": ("DDI %", "Meta DDI %"),
    "Desvio Benford %": ("Desvio Benford %", None),
    "Score ECI": ("Score ECI", None),
    "Taxa de Waivers": ("Taxa Waivers", None),
}


def _formato_hover(tipo: str) -> dict:
    if tipo == "pct":
        return dict(tickformat=".1%", hoverformat=".2%")
    if tipo == "dias":
        return dict(ticksuffix=" d", hoverformat=".1f")
    return dict(hoverformat=".2f")


def indicador_x_meta(d: Dados, r: Resultado) -> go.Figure:
    """Valor do indicador selecionado ao longo dos meses frente à meta.

    O risco residual não tem série mensal na planilha; para ele o gráfico mostra
    o risco residual de cada risco cadastrado frente à meta.
    """
    ind = r.indicador
    fig = go.Figure()

    if ind.chave not in SERIES_MENSAIS:
        riscos = d.riscos
        cores = [tema.COR_STATUS[avaliar(ind, v, r.meta)] for v in riscos["Risco Residual"]]
        fig.add_bar(x=riscos["ID"], y=riscos["Risco Residual"], name="Risco residual",
                    marker_color=cores, texttemplate="%{y:.1f}", textposition="outside",
                    textfont=dict(color=COR["texto"], size=12), cliponaxis=False,
                    customdata=riscos["Descrição do Risco"],
                    hovertemplate="%{x}: %{y:.1f}<br>%{customdata}<extra></extra>")
        fig.add_scatter(x=riscos["ID"], y=[r.meta] * len(riscos), mode="lines",
                        name=f"Meta ({f.curto(r.meta)})", line=_linha_meta(COR["texto"]))
        fig.update_layout(**tema.layout(bargap=0.45))
        fig.update_xaxes(**tema.EIXO_X)
        fig.update_yaxes(**tema.EIXO_Y, range=[0, max(riscos["Risco Residual"].max(), r.meta) * 1.2])
        return fig

    col_valor, col_meta = SERIES_MENSAIS[ind.chave]
    m = d.mensal
    valores = m[col_valor]
    metas = m[col_meta] if col_meta else [r.meta] * len(m)
    dentro = [ind.dentro(v, mt) for v, mt in zip(valores, metas)]
    cores = [COR["destaque"] if ok else COR["atencao"] for ok in dentro]
    fig.add_scatter(x=m["Mês"], y=valores, name=ind.titulo, mode="lines+markers",
                    line=dict(color=COR["destaque"], width=2.5),
                    marker=dict(color=cores, size=9, line=dict(color=COR["cartao"], width=2)))
    fig.add_scatter(x=m["Mês"], y=metas, name="Meta", mode="lines", line=_linha_meta(COR["texto"]))
    fig.add_scatter(x=[None], y=[None], mode="markers", name="Fora da meta",
                    marker=dict(color=COR["atencao"], size=9))
    todos = list(valores.dropna()) + [v for v in metas if v == v]
    folga = (max(todos) - min(todos)) * 0.15 or 1
    fig.update_layout(**tema.layout(**TEMPO))
    fig.update_xaxes(**tema.EIXO_X)
    fig.update_yaxes(**tema.EIXO_Y, range=[min(todos) - folga, max(todos) + folga], **_formato_hover(ind.tipo))
    return fig
