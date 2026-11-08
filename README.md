# Compliance Dashboard

Dashboard executivo para monitorar um programa de compliance, construído com **Python, Streamlit, Pandas e Plotly**. Os indicadores e gráficos são calculados a partir de uma planilha Excel, sem valores fixos no código.

<!-- Adicione aqui uma captura de tela da página para dar uma prévia visual:
![Prévia do dashboard](docs/preview.png) -->

## O que o projeto mostra

- **Seis cartões de indicadores**: ITR (treinamentos), TMI (tempo de investigação), DDI (due diligence), desvio de Benford, score ECI (cultura ética) e risco residual máximo. Cada cartão traz o valor atual, a meta e a situação: dentro da meta, atenção ou crítico.
- **Dez gráficos interativos**: evolução dos treinamentos, status dos indicadores, evolução do TMI, origem das denúncias, resultados das investigações, matriz de riscos, due diligence de fornecedores, cultura ética (radar), waivers e análise de Benford.
- **Detalhamento por clique**: ao clicar em uma linha de "Status dos indicadores", o gráfico ao lado passa a mostrar aquele indicador mês a mês contra a meta. Cada novo clique troca o indicador, e clicar fora volta ao gráfico original.
- **Visual próprio**, sem a aparência padrão do Streamlit: tema escuro, cartões em cinza, destaque turquesa e layout que se adapta a diferentes larguras de tela.

## Como executar

Requer Python 3.10 ou mais recente.

```bash
pip install -r requirements.txt
streamlit run app.py
```

O app abre em `http://localhost:8501`.

## Estrutura do projeto

```
.
├── app.py                  # página principal: monta o layout e liga os módulos
├── dashboard/
│   ├── dados.py            # leitura e tratamento da planilha
│   ├── indicadores.py      # definição dos indicadores e regra de situação (meta)
│   ├── graficos.py         # construção dos gráficos (Plotly)
│   ├── cartoes.py          # HTML do cabeçalho e dos cartões de indicador
│   ├── tema.py             # paleta de cores, CSS e layout base dos gráficos
│   └── formatos.py         # formatação de números no padrão pt-BR
├── dados/
│   └── compliance.xlsx     # fonte de dados
├── .streamlit/config.toml  # tema escuro do Streamlit
└── requirements.txt
```

A separação segue uma ideia simples: **dados**, **regras de negócio**, **visual** e **página** ficam em arquivos diferentes. Por exemplo, trocar uma meta ou a tolerância de um indicador mexe só em `indicadores.py`, e mudar uma cor mexe só em `tema.py`.


