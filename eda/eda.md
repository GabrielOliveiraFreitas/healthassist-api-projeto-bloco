# EDA — Dataset MedPT (HealthAssist API)

## Escolha do dataset

- **Nome:** MedPT (AKCIT/MedPT)
- **Fonte:** https://huggingface.co/datasets/AKCIT/MedPT — associado ao paper "MedPT: A Massive Medical Question Answering Dataset for Brazilian-Portuguese Speakers" (LREC 2026)
- **Licença:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Justificativa:** Dataset de interações reais entre pacientes e médicos, em português, com 384 mil perguntas de pacientes já classificadas por intenção (`question_type`, 7 categorias), o que se encaixa diretamente na proposta de triagem do HealthAssist. Foi selecionada uma amostra aleatória de 5.000 registros utilizando sample(n=5000, random_state=42), mantendo a reprodutibilidade da análise. O MedPT foi escolhido por representar interações entre pacientes e profissionais de saúde, contexto diretamente relacionado ao domínio do HealthAssist API. A coluna question representa a solicitação do usuário e question_type representa sua intenção semântica.

## Shape e tipos

- Shape: 5000 linhas x 6 colunas
- Colunas: `id` (int64), `question`, `answer`, `condition`, `medical_specialty`, `question_type` (todas texto)

## Valores ausentes e duplicatas

- Nenhum valor ausente em nenhuma coluna.
- Nenhuma linha totalmente duplicada. Embora a amostra contenha 5.000 registros, foram identificadas 1.646 perguntas distintas. Isso ocorre porque o dataset é composto por pares pergunta–resposta e uma mesma pergunta pode possuir múltiplas respostas médicas."

## Distribuição das categorias (question_type)

| Categoria | Quantidade |
|---|---|
| Tratamento | 2187 |
| Diagnóstico | 1653 |
| Escolha de profissionais de saúde | 376 |
| Epidemiologia | 321 |
| Estilo de vida saudável | 239 |
| Outros | 156 |
| Anatomia e fisiologia | 68 |

![Distribuição das categorias](grafico_categorias.png)

## Top 10 condições mais frequentes

Cefaleia (dor de cabeça), Fibromialgia, Disfunção da ATM, Bruxismo, Doença de Parkinson, Compulsão alimentar, Artrose, Esporão do Calcâneo, Bursite, Esclerose.

## Tamanho das perguntas

![Distribuição do tamanho das perguntas](grafico_tamanho_perguntas.png)

![Tamanho da pergunta por categoria](grafico_boxplot_categoria.png)

## Hipóteses sobre as intenções dos usuários

1. **Tratamento e Diagnóstico concentram quase 77% das perguntas** — sugere que a IA de triagem vai lidar majoritariamente com dois tipos de intenção: "o que eu tenho?" e "como eu resolvo isso?", enquanto categorias como Anatomia/Fisiologia são bem mais raras.
2. **Forte desbalanceamento entre categorias** (Tratamento tem ~32x mais exemplos que Anatomia e fisiologia) — ponto de atenção para a Parte 3: o classificador tende a ir mal nas categorias raras se não houver balanceamento ou reponderação.
3. **Perguntas de Diagnóstico e Escolha de profissionais de saúde tendem a ser mais longas** (mediana ~27 palavras) que as de Estilo de vida saudável (mediana ~12) — indica que pedir um diagnóstico exige descrever mais sintomas/contexto, enquanto perguntas sobre hábitos saudáveis são mais diretas.
