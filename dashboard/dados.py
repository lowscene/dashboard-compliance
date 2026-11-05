"""Leitura e tratamento da planilha de compliance.

A aba "Base de Dados & Lançamentos" tem vários blocos lado a lado (série mensal,
riscos, fornecedores, canais, trimestres, ECI e a tabela de KPIs). Em vez de
depender de posições fixas de linha/coluna, cada bloco é localizado pelo rótulo
do seu primeiro cabeçalho e lido até a primeira linha vazia. Se alguém inserir
linhas ou colunas na planilha, a leitura continua funcionando.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from . import formatos as f
from .indicadores import INDICADORES, POR_CHAVE, _fmt_valor

ABA_BASE = "Base de Dados & Lançamentos"
ARQUIVO_PADRAO = Path(__file__).resolve().parent.parent / "dados" / "compliance.xlsx"

COLUNAS_MENSAIS = [
    "Mês", "Treinamentos Elegíveis", "Treinamentos Concluídos", "ITR %", "Meta ITR %",
    "Denúncias Recebidas", "Casos Concluídos", "Dias Totais Investigação", "TMI", "SLA TMI",
    "Casos Procedentes", "Waivers Solicitados", "Waivers Aprovados", "Taxa Waivers",
    "Transações Analisadas", "Transações Fora Benford", "Desvio Benford %", "Score ECI",
    "DDI %", "Meta DDI %",
]
COLUNAS_RISCOS = [
    "ID", "Descrição do Risco", "Categoria", "Probabilidade (1-4)", "Impacto (1-4)",
    "Eficácia do Controle %", "Risco Residual",
]
COLUNAS_TRIMESTRES = ["Trimestre", "Procedente", "Improcedente", "Inconclusivo", "Em Aberto"]


@dataclass
class Dados:
    mensal: pd.DataFrame
    riscos: pd.DataFrame
    fornecedores: pd.DataFrame
    canais: pd.DataFrame
    trimestres: pd.DataFrame
    eci: pd.DataFrame
    kpis: dict[str, tuple[float, float]]   # {chave: (valor, meta)}
    avisos: list[str] = field(default_factory=list)

    @property
    def periodo(self) -> str:
        meses = self.mensal["Mês"]
        return f"{meses.iloc[0]} a {meses.iloc[-1]}"


# --------------------------------------------------------------------------- leitura
def _localizar(bruto: pd.DataFrame, rotulo: str) -> tuple[int, int]:
    valores = bruto.to_numpy(dtype=object)
    for r in range(valores.shape[0]):
        for c in range(valores.shape[1]):
            v = valores[r, c]
            if isinstance(v, str) and v.strip() == rotulo:
                return r, c
    raise KeyError(f"Não encontrei o bloco '{rotulo}' na aba '{ABA_BASE}'.")


def _ler_bloco(bruto: pd.DataFrame, ancora: str, texto: tuple[str, ...] = ()) -> pd.DataFrame:
    """Lê o bloco cujo primeiro cabeçalho é `ancora`.

    Colunas: da âncora para a direita até o primeiro cabeçalho vazio.
    Linhas: abaixo do cabeçalho até a primeira linha totalmente vazia.
    Colunas fora de `texto` são convertidas para número (inválidos viram NaN).
    """
    r, c = _localizar(bruto, ancora)
    colunas = []
    j = c
    while j < bruto.shape[1] and pd.notna(bruto.iat[r, j]):
        colunas.append(j)
        j += 1
    nomes = [str(bruto.iat[r, j]).strip() for j in colunas]

    corpo = bruto.iloc[r + 1:, colunas]
    vazias = corpo.isna().all(axis=1).to_numpy()
    fim = int(vazias.argmax()) if vazias.any() else len(corpo)
    bloco = corpo.iloc[:fim].copy()
    bloco.columns = nomes
    bloco = bloco.reset_index(drop=True)

    for nome in bloco.columns:
        if nome in texto:
            bloco[nome] = bloco[nome].astype(str).str.strip()
        else:
            bloco[nome] = pd.to_numeric(bloco[nome], errors="coerce")
    return bloco


def _exigir(df: pd.DataFrame, colunas: list[str], nome: str) -> None:
    faltando = [c for c in colunas if c not in df.columns]
    if faltando:
        raise KeyError(f"No bloco '{nome}' faltam as colunas: {', '.join(faltando)}.")


# --------------------------------------------------------------------------- KPIs
def _consolidar_kpis(mensal, riscos, tabela, avisos) -> dict[str, tuple[float, float]]:
    """Valor e meta de cada indicador.

    Usa a tabela KPI da planilha; se a linha não existir, calcula a partir da
    série mensal. Quando os dois existem e divergem, avisa.
    """
    calculado = {
        "ITR %": mensal["ITR %"].mean(),
        "TMI (Dias)": mensal["TMI"].mean(),
        "DDI %": mensal["DDI %"].mean(),
        "Desvio Benford %": mensal["Desvio Benford %"].mean(),
        "Score ECI": mensal["Score ECI"].mean(),
        "Taxa de Waivers": mensal["Taxa Waivers"].mean(),
        "Risco Residual Máx": riscos["Risco Residual"].max(),
    }
    metas_mensais = {
        "ITR %": mensal["Meta ITR %"].mean(),
        "TMI (Dias)": mensal["SLA TMI"].mean(),
        "DDI %": mensal["Meta DDI %"].mean(),
    }
    kpis = {}
    for ind in INDICADORES:
        k = ind.chave
        na_tabela = tabela is not None and k in tabela.index
        valor = tabela.loc[k, "Valor"] if na_tabela else float("nan")
        meta = tabela.loc[k, "Meta"] if na_tabela else float("nan")
        if pd.isna(valor):
            valor = calculado[k]
        elif not pd.isna(calculado[k]) and abs(valor - calculado[k]) > 0.005 * abs(calculado[k]) + 1e-9:
            num_a, _ = _fmt_valor(ind.tipo, valor)
            num_b, _ = _fmt_valor(ind.tipo, calculado[k])
            avisos.append(
                f"{ind.titulo}: a tabela de KPIs da planilha mostra {num_a}, mas a série "
                f"mensal resulta em {num_b}. O painel usa o valor da tabela."
            )
        if pd.isna(meta):
            meta = metas_mensais.get(k, float("nan"))
        kpis[k] = (float(valor), float(meta))
    return kpis


# --------------------------------------------------------------------------- avisos
def _avisos(mensal, riscos, canais, trimestres, kpis) -> list[str]:
    av: list[str] = []

    ausentes = mensal[COLUNAS_MENSAIS[1:]].isna().sum()
    ausentes = ausentes[ausentes > 0]
    if len(ausentes):
        av.append(
            "Há valores ausentes na série mensal: "
            + ", ".join(f"{k} ({v})" for k, v in ausentes.items()) + "."
        )

    total_canais = canais["Quantidade"].sum()
    total_denuncias = mensal["Denúncias Recebidas"].sum()
    if total_canais != total_denuncias:
        av.append(
            f"A origem das denúncias soma {f.num(total_canais)} relatos, mas a série mensal "
            f"registra {f.num(total_denuncias)} denúncias recebidas."
        )

    encerrados = trimestres[["Procedente", "Improcedente", "Inconclusivo"]].sum().sum()
    concluidos = mensal["Casos Concluídos"].sum()
    if encerrados != concluidos:
        av.append(
            f"Os resultados por trimestre somam {f.num(encerrados)} casos encerrados "
            f"(procedentes, improcedentes e inconclusivos), enquanto a série mensal "
            f"registra {f.num(concluidos)} casos concluídos."
        )

    esperado = (
        riscos["Probabilidade (1-4)"] * riscos["Impacto (1-4)"]
        * (1 - riscos["Eficácia do Controle %"])
    )
    if ((esperado - riscos["Risco Residual"]).abs() > 0.01).any():
        av.append("O risco residual da planilha não segue Probabilidade × Impacto × (1 − eficácia).")
    if "Risco Residual 2" in riscos.columns and (riscos["Risco Residual 2"] < 0).any():
        av.append(
            "A coluna 'Risco Residual 2' tem valores negativos e não é usada no painel; "
            "o risco residual considerado é o da coluna 'Risco Residual'."
        )

    # Os valores do painel são médias simples dos meses; compara com o total do período.
    agregados = {
        "ITR %": mensal["Treinamentos Concluídos"].sum() / mensal["Treinamentos Elegíveis"].sum(),
        "TMI (Dias)": mensal["Dias Totais Investigação"].sum() / mensal["Casos Concluídos"].sum(),
        "Desvio Benford %": mensal["Transações Fora Benford"].sum() / mensal["Transações Analisadas"].sum(),
        "Taxa de Waivers": mensal["Waivers Aprovados"].sum() / mensal["Waivers Solicitados"].sum(),
    }
    for chave, total in agregados.items():
        ind = POR_CHAVE[chave]
        valor, meta = kpis[chave]
        if pd.isna(total) or pd.isna(valor) or abs(total - valor) <= 0.001 * abs(valor):
            continue
        txt = (
            f"{ind.titulo}: o painel usa a média simples dos meses ({_fmt_valor(ind.tipo, valor)[0]}); "
            f"calculado sobre o total do período seria {_fmt_valor(ind.tipo, total)[0]}."
        )
        if not pd.isna(meta) and ind.dentro(valor, meta) != ind.dentro(total, meta):
            txt += " Essa diferença muda a situação frente à meta."
        av.append(txt)
    return av


# --------------------------------------------------------------------------- API
def carregar(caminho: Path | str | None = None) -> Dados:
    caminho = Path(caminho or ARQUIVO_PADRAO)
    if not caminho.exists():
        raise FileNotFoundError(f"Planilha não encontrada: {caminho}")

    bruto = pd.read_excel(caminho, sheet_name=ABA_BASE, header=None)

    mensal = _ler_bloco(bruto, "Mês", texto=("Mês",))
    _exigir(mensal, COLUNAS_MENSAIS, "série mensal")
    riscos = _ler_bloco(bruto, "ID", texto=("ID", "Descrição do Risco", "Categoria"))
    _exigir(riscos, COLUNAS_RISCOS, "riscos")
    fornecedores = _ler_bloco(bruto, "Categoria Fornecedor", texto=("Categoria Fornecedor",))
    canais = _ler_bloco(bruto, "Canal", texto=("Canal",))
    trimestres = _ler_bloco(bruto, "Trimestre", texto=("Trimestre",))
    _exigir(trimestres, COLUNAS_TRIMESTRES, "resultados por trimestre")
    eci = _ler_bloco(bruto, "Dimensão Organizacional", texto=("Dimensão Organizacional",))

    try:
        tabela = _ler_bloco(bruto, "KPI", texto=("KPI",)).set_index("KPI")
    except KeyError:
        tabela = None

    avisos: list[str] = []
    kpis = _consolidar_kpis(mensal, riscos, tabela, avisos)
    avisos += _avisos(mensal, riscos, canais, trimestres, kpis)
    return Dados(mensal, riscos, fornecedores, canais, trimestres, eci, kpis, avisos)
