"""Definição dos indicadores, regras de situação frente à meta e formatação.

As metas vêm da planilha. O que fica aqui é apenas a *interpretação*:
se o indicador é melhor quando maior ou menor e qual a tolerância
para classificar como "atenção" antes de virar "crítico".
Ajuste `tolerancia` conforme a política da empresa.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from . import formatos as f

STATUS_ROTULO = {
    "ok": "Dentro da meta",
    "atencao": "Atenção",
    "critico": "Crítico",
    "sem_meta": "Sem meta",
}


@dataclass(frozen=True)
class Indicador:
    chave: str            # rótulo exato na tabela KPI da planilha
    titulo: str           # nome no cartão
    descricao: str        # descrição curta
    rotulo: str           # nome curto para gráficos
    tipo: str             # 'pct' | 'dias' | 'score'
    menor_melhor: bool    # True: valor abaixo da meta é bom (TMI, Benford...)
    tolerancia: float     # faixa de "atenção", como fração da meta

    def dentro(self, valor: float, meta: float) -> bool:
        return valor <= meta if self.menor_melhor else valor >= meta


INDICADORES: list[Indicador] = [
    Indicador("ITR %", "ITR", "Índice de Treinamentos Realizados", "ITR", "pct", False, 0.10),
    Indicador("TMI (Dias)", "TMI", "Tempo Médio de Investigação", "TMI", "dias", True, 0.15),
    Indicador("DDI %", "DDI", "Due Diligence de Integridade", "DDI", "pct", False, 0.10),
    Indicador("Desvio Benford %", "Desvio Benford", "Transações fora do padrão de Benford",
              "Benford", "pct", True, 0.20),
    Indicador("Score ECI", "Score ECI", "Índice de Cultura Ética", "ECI", "score", False, 0.20),
    Indicador("Taxa de Waivers", "Taxa de Waivers", "Waivers aprovados sobre solicitados",
              "Waivers", "pct", True, 0.50),
    Indicador("Risco Residual Máx", "Risco Residual Máximo", "Maior risco residual da matriz",
              "Risco residual", "score", True, 0.50),
]
POR_CHAVE = {i.chave: i for i in INDICADORES}

# Indicadores que aparecem nos cartões do topo (a taxa de waivers tem gráfico próprio).
PRINCIPAIS = (
    "ITR %", "TMI (Dias)", "DDI %", "Desvio Benford %", "Score ECI", "Risco Residual Máx",
)


@dataclass(frozen=True)
class Resultado:
    indicador: Indicador
    valor: float
    meta: float
    status: str
    atingimento: float     # 1.0 = meta atingida (para menor_melhor, usa meta/valor)
    valor_num: str         # '93,46%' | '30,13' | '4,34'
    unidade: str           # 'dias' ou ''
    valor_fmt: str         # valor com unidade
    meta_fmt: str


def _fmt_valor(tipo: str, v: float) -> tuple[str, str]:
    if tipo == "pct":
        return f.pct(v, 2), ""
    if tipo == "dias":
        return f.num(v, 2), "dias"
    return f.num(v, 2), ""


def _fmt_meta(tipo: str, v: float) -> str:
    if pd.isna(v):
        return ""
    if tipo == "pct":
        return f.pct_curto(v)
    if tipo == "dias":
        return f"{f.curto(v)} dias"
    return f.curto(v)


def avaliar(ind: Indicador, valor: float, meta: float) -> str:
    if pd.isna(valor) or pd.isna(meta) or meta == 0:
        return "sem_meta"
    if ind.dentro(valor, meta):
        return "ok"
    limite = meta * (1 + ind.tolerancia) if ind.menor_melhor else meta * (1 - ind.tolerancia)
    em_atencao = valor <= limite if ind.menor_melhor else valor >= limite
    return "atencao" if em_atencao else "critico"


def atingimento(ind: Indicador, valor: float, meta: float) -> float:
    if pd.isna(valor) or pd.isna(meta) or meta == 0 or valor == 0:
        return float("nan")
    return meta / valor if ind.menor_melhor else valor / meta


def montar_resultados(kpis: dict[str, tuple[float, float]]) -> list[Resultado]:
    """kpis: {chave: (valor, meta)} -> lista de Resultado na ordem de INDICADORES."""
    resultados = []
    for ind in INDICADORES:
        if ind.chave not in kpis:
            continue
        valor, meta = kpis[ind.chave]
        num, unidade = _fmt_valor(ind.tipo, valor)
        resultados.append(
            Resultado(
                indicador=ind,
                valor=valor,
                meta=meta,
                status=avaliar(ind, valor, meta),
                atingimento=atingimento(ind, valor, meta),
                valor_num=num,
                unidade=unidade,
                valor_fmt=f"{num} {unidade}".strip(),
                meta_fmt=_fmt_meta(ind.tipo, meta),
            )
        )
    return resultados
