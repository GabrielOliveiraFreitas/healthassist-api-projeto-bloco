# Planejamento T2 — fase preditiva (HealthAssist API)

## (a) Modelo candidato

**Regressão logística multinomial** como modelo principal, e **SVM linear** (`LinearSVC`) como comparação.

Escolhi a regressão logística porque:
- funciona bem com texto representado em TF-IDF (muitas colunas, quase todas zeradas);
- dá a probabilidade de cada classe, que combina com a resposta do `/predict`;
- os coeficientes mostram quais palavras puxam para cada classe, o que ajuda a explicar o modelo na banca.

Vou usar `class_weight="balanced"` por causa do desbalanceamento (Tratamento 43,7% contra Anatomia e fisiologia 1,4%).

## (b) Estratégia de features para texto

- **TF-IDF** (`TfidfVectorizer`) sobre a coluna `question`, com unigramas e bigramas (`ngram_range=(1, 2)`) e `min_df=2` para cortar palavras muito raras.
- Texto em minúsculas e `strip_accents="unicode"`, porque os pacientes escrevem com erros e sem acento.
- Stopwords em português, testando com e sem para ver se muda o resultado (palavras como "como" e "qual" podem ser justamente o sinal de algumas intenções).
- `CountVectorizer` como alternativa de comparação com o TF-IDF.
- Ficam fora as features de tamanho do texto usadas no TP2/TP3, já que mostraram pouca relação com o que quero prever.

**Avaliação:** separar treino e teste agrupando pela pergunta (`StratifiedGroupKFold` ou `GroupShuffleSplit`), para não vazar a mesma pergunta entre os dois lados. Métrica principal: F1 macro, mais recall por classe e matriz de confusão.

## (c) Colega adversário

A definir após o sorteio da dupla adversária no final do TP3.

- Dupla/colega adversário: _______________________

## (d) URL ou IP da API adversária (alvo do TP4/TP5)

A trocar com a dupla adversária junto com o arquivo OpenAPI/Swagger.

- URL/IP da API alvo: _______________________
- Arquivo OpenAPI/Swagger recebido: [ ] sim  [ ] não

> Os itens (c) e (d) dependem do sorteio e são da dupla, então precisam ser preenchidos junto com o colega.
