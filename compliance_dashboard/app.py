"""Compliance Dashboard: página inicial do Dashboard Executivo.

Execute com:  streamlit run app.py
"""
from __future__ import annotations

import inspect
from pathlib import Path

import streamlit as st

from dashboard import cartoes, graficos, tema
from dashboard.dados import ARQUIVO_PADRAO, carregar
from dashboard.indicadores import montar_resultados

st.set_page_config(
    page_title="Compliance Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CONFIG_GRAFICO = {"displayModeBar": False, "responsive": True}
# `width="stretch"` substitui `use_container_width` nas versões recentes do Streamlit.
_USA_WIDTH = "width" in inspect.signature(st.plotly_chart).parameters


@st.cache_data(show_spinner=False)
def _carregar(caminho: str, assinatura: float):
    """O parâmetro `assinatura` (data de modificação) renova o cache quando a planilha muda."""
    return carregar(Path(caminho))


CHAVE_SELECAO = "sel_status"   # estado do clique no gráfico "Status dos indicadores"


def mostrar(fig, **opcoes) -> None:
    if _USA_WIDTH:
        st.plotly_chart(fig, width="stretch", theme=None, config=CONFIG_GRAFICO, **opcoes)
    else:
        st.plotly_chart(fig, use_container_width=True, theme=None, config=CONFIG_GRAFICO, **opcoes)


def cartao(chave: str, titulo: str, subtitulo: str, fig, **opcoes) -> None:
    with st.container(key=f"card_{chave}"):
        st.markdown(cartoes.titulo_card(titulo, subtitulo), unsafe_allow_html=True)
        mostrar(fig, **opcoes)


def indicador_selecionado(resultados):
    """Resultado da linha clicada em "Status dos indicadores", ou None.

    O estado do clique fica em st.session_state desde a execução anterior;
    por isso pode ser lido antes de o gráfico ser desenhado.
    """
    estado = st.session_state.get(CHAVE_SELECAO)
    try:
        pontos = estado["selection"]["points"]
    except (KeyError, TypeError):
        return None
    if not pontos:
        return None
    itens = graficos.itens_status(resultados)
    posicao = pontos[-1].get("point_index")
    if posicao is None or not 0 <= posicao < len(itens):
        return None
    return itens[posicao]


def html(conteudo: str) -> None:
    st.markdown(conteudo, unsafe_allow_html=True)


# --------------------------------------------------------------------------- dados
html(f"<style>{tema.css()}</style>")

try:
    arquivo = Path(ARQUIVO_PADRAO)
    dados = _carregar(str(arquivo), arquivo.stat().st_mtime if arquivo.exists() else 0.0)
except (FileNotFoundError, KeyError, ValueError) as erro:
    st.error(f"Não foi possível ler a planilha de compliance. {erro}")
    st.stop()

resultados = montar_resultados(dados.kpis)

# --------------------------------------------------------------------------- cabeçalho e indicadores
html(cartoes.cabecalho(dados.periodo, resultados))
html(cartoes.secao(
    "Indicadores principais",
    "Valores consolidados do período, comparados à meta de cada indicador.",
))
html(cartoes.grade_indicadores(resultados))

# --------------------------------------------------------------------------- gráficos
html(cartoes.secao("Desempenho do programa"))
selecionado = indicador_selecionado(resultados)
c1, c2 = st.columns([3, 2])
with c1:
    if selecionado is None:
        cartao("treinamentos", "Evolução dos treinamentos",
               "Treinamentos concluídos e elegíveis por mês, com o ITR frente à meta.",
               graficos.treinamentos(dados))
    else:
        if selecionado.indicador.chave in graficos.SERIES_MENSAIS:
            detalhe = "Valor mensal frente à meta; clique em outra linha ao lado para trocar."
        else:
            detalhe = ("Cada risco frente à meta (este indicador não tem série mensal); "
                       "clique em outra linha para trocar.")
        cartao("treinamentos", f"{selecionado.indicador.titulo} × meta", detalhe,
               graficos.indicador_x_meta(dados, selecionado))
with c2:
    cartao("status", "Status dos indicadores",
           "Percentual da meta atingido, colorido pela situação. "
           "Clique em uma linha para ver o indicador mês a mês no gráfico de evolução.",
           graficos.status_indicadores(resultados),
           on_select="rerun", selection_mode="points", key=CHAVE_SELECAO)

html(cartoes.secao("Denúncias e investigações"))
c1, c2, c3 = st.columns(3)
with c1:
    cartao("tmi", "Evolução do TMI",
           "Tempo médio de investigação por mês, com a linha de referência.",
           graficos.tmi(dados))
with c2:
    cartao("origem", "Origem das denúncias",
           "Distribuição dos relatos por canal de recebimento.",
           graficos.origem_denuncias(dados))
with c3:
    cartao("resultados", "Resultados das investigações",
           "Casos por trimestre, segundo o resultado da apuração.",
           graficos.resultados_investigacoes(dados))

html(cartoes.secao("Riscos, terceiros e cultura"))
c1, c2, c3 = st.columns(3)
with c1:
    cartao("matriz", "Matriz de riscos",
           "Probabilidade e impacto; cada número identifica um risco.",
           graficos.matriz_riscos(dados))
with c2:
    cartao("ddi", "Due diligence de fornecedores",
           "Percentual de due diligence por categoria de fornecedor.",
           graficos.due_diligence(dados))
with c3:
    cartao("eci", "Cultura ética",
           "Score do ECI em cada dimensão organizacional.",
           graficos.cultura_etica(dados))

html(cartoes.secao("Exceções e análise de transações"))
c1, c2 = st.columns(2)
with c1:
    cartao("waivers", "Waivers",
           "Solicitações e aprovações por mês, com a taxa de waivers frente à meta.",
           graficos.waivers(dados))
with c2:
    cartao("benford", "Análise de Benford",
           "Volume de transações analisadas e percentual fora do padrão por mês.",
           graficos.benford(dados))
