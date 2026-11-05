import pandas as pd
import streamlit as st

# Lendo a planilha
arquivo = "dados/compliance.xlsx"

dados = pd.read_excel(
    arquivo,
    sheet_name="Base de Dados & Lançamentos",
    header=1
)

# Exibindo os dados
st.title("Dashboard de Compliance")

st.subheader("Base de dados")
st.dataframe(dados)




st.title("Dashboard Executivo de Compliance")

st.subheader("Indicadores principais")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("ITR", "93,46%")

with col2:
    st.metric("TMI", "30,13 dias")

with col3:
    st.metric("DDI", "93,75%")