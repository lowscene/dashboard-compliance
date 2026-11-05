"""Blocos HTML da página: cabeçalho, títulos de seção e cartões de indicador.

Atenção: o HTML é passado a st.markdown, cujo parser trata linhas em branco e
recuo de 4 espaços de forma especial. Por isso as strings abaixo são montadas
em uma única linha, sem indentação.
"""
from __future__ import annotations

from html import escape

from .indicadores import PRINCIPAIS, STATUS_ROTULO, Resultado


def _rotulo_contagem(status: str, n: int) -> str:
    if status == "ok":
        return "dentro da meta"
    if status == "atencao":
        return "em atenção"
    return "crítico" if n == 1 else "críticos"


def cabecalho(periodo: str, resultados: list[Resultado]) -> str:
    principais = [r for r in resultados if r.indicador.chave in PRINCIPAIS]
    chips = ""
    for status in ("ok", "atencao", "critico"):
        n = sum(1 for r in principais if r.status == status)
        chips += (
            f'<span class="cd-chip"><i style="background:var(--{status})"></i>'
            f"<b>{n}</b>{_rotulo_contagem(status, n)}</span>"
        )
    return (
        '<div class="cd-header"><div>'
        '<div class="cd-sistema"><span class="cd-marca"></span>Compliance Dashboard</div>'
        '<div class="cd-h1" role="heading" aria-level="1">Dashboard Executivo</div>'
        f'<div class="cd-lead">Monitoramento mensal do programa de compliance, de {escape(periodo)}.</div>'
        f'</div><div class="cd-resumo">{chips}</div></div>'
    )


def secao(titulo: str, subtitulo: str = "") -> str:
    sub = f'<div class="cd-secao-s">{escape(subtitulo)}</div>' if subtitulo else ""
    return f'<div class="cd-secao"><div class="cd-secao-t">{escape(titulo)}</div>{sub}</div>'


def titulo_card(titulo: str, subtitulo: str) -> str:
    return (
        f'<div class="cd-titulo">{escape(titulo)}</div>'
        f'<div class="cd-sub">{escape(subtitulo)}</div>'
    )


def _cartao(r: Resultado) -> str:
    ind = r.indicador
    if r.meta_fmt:
        prefixo = "Meta máxima" if ind.menor_melhor else "Meta mínima"
        meta = f"{prefixo} {escape(r.meta_fmt)}"
    else:
        meta = "Sem meta definida"
    unidade = f"<small>{escape(r.unidade)}</small>" if r.unidade else ""
    return (
        f'<div class="cd-kpi cd-kpi--{r.status}">'
        f'<div class="cd-kpi-topo"><div class="cd-kpi-titulo">{escape(ind.titulo)}</div>'
        f'<span class="cd-pill cd-{r.status}"><i></i>{STATUS_ROTULO[r.status]}</span></div>'
        f'<div class="cd-kpi-desc">{escape(ind.descricao)}</div>'
        f'<div class="cd-kpi-valor">{escape(r.valor_num)}{unidade}</div>'
        f'<div class="cd-kpi-meta">{meta}</div>'
        "</div>"
    )


def grade_indicadores(resultados: list[Resultado]) -> str:
    por_chave = {r.indicador.chave: r for r in resultados}
    cartoes = "".join(_cartao(por_chave[k]) for k in PRINCIPAIS if k in por_chave)
    return f'<div class="cd-grade">{cartoes}</div>'
