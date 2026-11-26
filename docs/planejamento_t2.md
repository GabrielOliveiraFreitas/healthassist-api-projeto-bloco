# Planejamento T2 — fase preditiva (HealthAssist API)

> Documento consolidado (TP3). Reúne o planejamento preditivo da branch de dados
> (`parte-dados-tp3`) com a definição do adversário do TP4. Substitui as versões
> anteriores que existiam em `docs/` (pentest) e em `eda/planejamento_t2.md`.

## (a) Modelo candidato

**Regressão logística multinomial** como modelo principal, e **SVM linear**
(`LinearSVC`) como comparação.

Escolhi a regressão logística porque:

- funciona bem com texto representado em TF-IDF (muitas colunas, quase todas zeradas);
- dá a probabilidade de cada classe, que combina com a resposta do `/predict`/`/classify`;
- os coeficientes mostram quais palavras puxam para cada classe, o que ajuda a
  explicar o modelo na banca.

Vou usar `class_weight="balanced"` por causa do desbalanceamento (Tratamento
43,7% contra Anatomia e fisiologia 1,4%). O `LinearSVC` entra como baseline de
comparação por costumar ir bem em classificação de texto esparso de alta dimensão.

## (b) Estratégia de feature engineering para texto

- **TF-IDF** (`TfidfVectorizer`) sobre a coluna `question`, com unigramas e
  bigramas (`ngram_range=(1, 2)`) e `min_df=2` para cortar palavras muito raras.
- Texto em minúsculas e `strip_accents="unicode"`, porque os pacientes escrevem
  com erros e sem acento.
- Stopwords em português, testando com e sem para ver se muda o resultado
  (palavras como "como" e "qual" podem ser justamente o sinal de algumas intenções).
- **TF-IDF vs CountVectorizer:** uso TF-IDF como padrão porque reduz o peso de
  termos muito frequentes e genéricos; mantenho `CountVectorizer` como alternativa
  de comparação.
- Ficam fora as features de tamanho do texto usadas no TP2/TP3 (tam_pergunta,
  palavras_unicas), já que a regressão mostrou que elas têm pouca relação com o
  alvo (R² ~0).

**Avaliação:** separar treino e teste agrupando pela pergunta
(`StratifiedGroupKFold` ou `GroupShuffleSplit`), para não vazar a mesma pergunta
entre os dois lados. Métrica principal: **F1 macro**, mais recall por classe e
matriz de confusão (acurácia é enganosa pelo forte desbalanceamento).

## (c) Colega adversário

**Helena Gomes** — projeto **TourShield API**.

Troca de alvos autorizada e mútua dentro da disciplina (laboratório acadêmico,
sem sistema de produção envolvido). Cada dupla disponibiliza sua API com usuários
de seed e o arquivo OpenAPI/Swagger para a outra.

- Dupla/colega adversário: **Helena Gomes (TourShield API)**

## (d) URL/IP da API adversária (alvo do TP4/TP5)

- URL/IP da API alvo: **http://127.0.0.1:8800**
- App alvo: **TourShield API v0.4.0** (FastAPI), laboratório local da colega Helena Gomes.
- Arquivo OpenAPI/Swagger recebido: [x] sim — disponível em `GET /openapi.json`
  e `GET /docs` (Swagger self-hosted) do alvo.

Regras de escopo: atacar somente o alvo autorizado, em laboratório local; não
reiniciar nem derrubar o serviço; evidenciar tanto ataques bem-sucedidos quanto
os que falham (explicando qual defesa atuou).

## Pendências / próximos passos

- [ ] Treinar e versionar o classificador (LogisticRegression/SVM) e ligá-lo ao
      `/classify` / `/predict`.
- [ ] Carregar o artefato do modelo a partir de caminho fixo e origem confiável
      (desserialização de modelo é vetor de execução de código) e **não logar
      sintomas** (LGPD de saúde).
- [ ] Ativar *branch protection* exigindo o check `gates` no GitHub.
