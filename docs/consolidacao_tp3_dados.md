# Consolidação TP3 — artefatos estatísticos / de dados

Este documento registra a consolidação, na working tree da `main`, dos artefatos
estatísticos que estavam apenas na branch remota `parte-dados-tp3` (apontado no
feedback do professor como "não consolidado na main"). Todos os arquivos foram
extraídos via `git show parte-dados-tp3:<path>` para os mesmos caminhos relativos.

## 1. Arquivos consolidados a partir de `parte-dados-tp3`

**EDA / estatística (`eda/`):**

- `eda/regressao_medpt.ipynb` — notebook de regressão linear (simples + múltipla).
- `eda/qq_plot.png`, `eda/residual_plot.png` — gráficos de diagnóstico de resíduos.
- `eda/eda.md`, `eda/eda_report.md`, `eda/eda_report_tp2.md` — relatórios de EDA.
- `eda/eda_medpt_tp2.py` — script de EDA do TP2.
- `eda/medpt_amostra.csv` — amostra de 5.000 linhas do dataset MedPT.
- `eda/dfd_cia.md` — notas de DFD/CIA (também presente em `docs/`).

**Documentação (`docs/`):**

- `docs/documento_pergunta_classificacao.md` — formalização da pergunta de classificação.
- `docs/dfd_cia.md` — DFD/CIA.
- `docs/imagens dos gráficos/` — 7 PNGs de EDA (categorias, boxplot, tamanho das
  perguntas, heatmap de correlação, scatters, diagrama de reserva).

**Novos / consolidados nesta rodada:**

- `eda/regressao_tp3.py` — versão em **script reprodutível** do notebook (execução
  não interativa, backend matplotlib `Agg`, gera os PNGs). Reproduz exatamente os
  números do notebook.
- `docs/planejamento_t2.md` — **consolidado** (substitui a versão de pentest da
  `main` e o duplicado `eda/planejamento_t2.md`, que foi removido). Agora traz
  modelo candidato, feature engineering, colega adversário e URL do alvo.

## 2. Resultados numéricos (regressão linear — alvo: `tam_resposta`)

Validados executando `eda/regressao_tp3.py` (idênticos aos outputs salvos no notebook):

| Modelo | Features | R² (teste) | RMSE (teste) |
|---|---|---|---|
| Simples | `tam_pergunta` | **0,0029** | **36,34** |
| Múltipla | `tam_pergunta`, `palavras_unicas`, `num_interrogacoes` + `question_type` (one-hot) | **0,0061** | **36,28** |

Split: `GroupShuffleSplit` agrupado pela pergunta (4.063 treino / 937 teste).
Assimetria (skew) dos resíduos ≈ **1,99** (cauda longa à direita → violação das
premissas da regressão linear). Conclusão: R² ~0 — o tamanho do texto quase não
explica o tamanho da resposta; a regressão linear é inadequada e a tarefa real do
projeto é de **classificação de intenção**.

## 3. Checklist de evidências obrigatórias do TP3

| Evidência | Status | Onde |
|---|---|---|
| Notebook de regressão | OK | `eda/regressao_medpt.ipynb` (+ script `eda/regressao_tp3.py`) |
| Pré-processamento | OK | variáveis derivadas + `StandardScaler` + `OneHotEncoder` |
| Regressão linear MÚLTIPLA (>1 feature) | OK | célula 9 (3 numéricas + `question_type`) |
| Cálculo de R² | OK | 0,0029 (simples) / 0,0061 (múltipla) |
| Cálculo de RMSE | OK | 36,34 (simples) / 36,28 (múltipla) |
| Residual plot | OK | `eda/residual_plot.png` (regenerado) |
| Q-Q plot | OK | `eda/qq_plot.png` (regenerado) |
| Seção de limitações | OK | notebook (cél. 14-15) + `regressao_tp3.py` |
| Documento de pergunta de classificação | OK | `docs/documento_pergunta_classificacao.md` |
| — pergunta + classes + distribuição | OK | 7 intenções, tabela de distribuição |
| — por que regressão linear não serve p/ classificação | OK | seção 4 (justifica LogReg/SVM) |
| Planejamento T2 — modelo candidato | OK | `docs/planejamento_t2.md` (a) LogReg + SVM |
| Planejamento T2 — feature engineering | OK | (b) TF-IDF vs CountVectorizer, n-grams |
| Planejamento T2 — colega adversário | OK | (c) **Helena Gomes (TourShield API)** |
| Planejamento T2 — URL/IP do alvo | OK | (d) **http://127.0.0.1:8800** (TourShield v0.4.0) |

Nenhuma evidência obrigatória ficou faltando. Observação: o `.venv` do repositório
não possui as libs de ciência de dados; a reprodução do notebook foi feita em um
venv auxiliar com pandas/scikit-learn/scipy/matplotlib, mas o script
`eda/regressao_tp3.py` roda em qualquer ambiente com essas dependências.
