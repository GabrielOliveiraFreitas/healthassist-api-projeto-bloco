# Classificação de Intenções (question_type) — TP4

## 1. Pergunta de modelagem

Dado o texto livre de uma pergunta médica em português (coluna `question`), **qual é a intenção do usuário** (coluna `question_type`)? Trata-se de uma classificação multiclasse com **7 classes**.

## 2. Classes e distribuição

Dataset: `eda/medpt_amostra.csv` — 5000 linhas, 1646 perguntas únicas (cada pergunta aparece ~3.0x, pois há múltiplas respostas por pergunta).

| Classe | Linhas | % linhas | Perguntas únicas |
|---|---:|---:|---:|
| Tratamento | 2187 | 43.7% | 671 |
| Diagnóstico | 1653 | 33.1% | 604 |
| Escolha de profissionais de saúde | 376 | 7.5% | 114 |
| Epidemiologia | 321 | 6.4% | 118 |
| Estilo de vida saudável | 239 | 4.8% | 62 |
| Outros | 156 | 3.1% | 52 |
| Anatomia e fisiologia | 68 | 1.4% | 25 |

O conjunto é **fortemente desbalanceado**: _Tratamento_ e _Diagnóstico_ somam a grande maioria, enquanto _Anatomia e fisiologia_ tem apenas ~25 perguntas únicas.

## 3. Pipeline

- **Pré-processamento + Vetorização**: `TfidfVectorizer` recebe o texto cru e aplica, com parâmetros nativos, minúsculas (`lowercase=True`), remoção de acentos (`strip_accents="unicode"`) e um `token_pattern` que mantém apenas tokens alfabéticos de 2+ letras, além de stopwords em português e `sublinear_tf=True`. Usar parâmetros nativos (em vez de uma função Python) deixa o `.joblib` **autossuficiente**: o endpoint `/classify` só precisa do scikit-learn para carregá-lo.
- **Classificador**: `LogisticRegression` multinomial com `class_weight="balanced"` (expõe `predict_proba`, requisito do contrato do endpoint `/classify`).
- **Split sem vazamento**: `GroupShuffleSplit` com `groups=question` (75/25) — treino=3793, teste=1207. A mesma pergunta nunca aparece em treino e teste.
- **Validação cruzada**: `StratifiedGroupKFold(n_splits=4)` dentro do `GridSearchCV` (respeita grupos e estratifica por classe).

## 4. GridSearchCV — melhores hiperparâmetros

Busca em grade (`scoring="f1_macro"`, 3×3×3 = 27 combinações × 4 folds):

| Hiperparâmetro | Valores testados | Melhor |
|---|---|---|
| `tfidf__ngram_range` | (1,1), (1,2), (1,3) | (1, 1) |
| `tfidf__min_df` | 1, 2, 3 | 3 |
| `clf__C` | 0.1, 1, 10 | 1.0 |

Melhor **F1-macro na validação cruzada**: **0.430**.

## 5. Métricas por classe (conjunto de teste)

| Classe | Precisão | Recall | F1 | Suporte |
|---|---:|---:|---:|---:|
| Anatomia e fisiologia | 0.148 | 0.182 | 0.163 | 22 |
| Diagnóstico | 0.741 | 0.801 | 0.770 | 407 |
| Epidemiologia | 0.443 | 0.595 | 0.508 | 79 |
| Escolha de profissionais de saúde | 0.720 | 0.628 | 0.671 | 86 |
| Estilo de vida saudável | 0.702 | 0.371 | 0.485 | 89 |
| Outros | 0.200 | 0.250 | 0.222 | 16 |
| Tratamento | 0.823 | 0.797 | 0.810 | 508 |

- **F1-macro**: **0.518**
- **Acurácia**: **0.723**

## 6. Comparação com baseline

| Modelo | F1-macro | Acurácia |
|---|---:|---:|
| Baseline (`DummyClassifier` most_frequent) | 0.085 | 0.421 |
| **TF-IDF + LogisticRegression** | **0.518** | **0.723** |

O modelo supera a baseline em **0.434** de F1-macro (0.085 → 0.518). A baseline atinge acurácia de 0.421 apenas prevendo sempre a classe majoritária, mas seu F1-macro é baixíssimo — isso ilustra por que **a acurácia sozinha engana** num problema tão desbalanceado, e por que escolhemos F1-macro como métrica principal.

## 7. Matriz de confusão

Ver `eda/matriz_confusao.png` (contagens no conjunto de teste). As confusões concentram-se entre _Tratamento_ e _Diagnóstico_ (classes majoritárias e semanticamente próximas) e nas classes minoritárias, que têm pouquíssimos exemplos.

## 8. Limitações

- **Desbalanceamento severo**: _Anatomia e fisiologia_ tem ~25 perguntas únicas; o recall nessas classes é instável.
- **Rótulos ruidosos**: a fronteira entre _Tratamento_, _Diagnóstico_ e _Outros_ é subjetiva; há sobreposição semântica real.
- **Português informal**: erros de digitação, abreviações e gírias não são corrigidos; apenas normalização básica é aplicada.
- **Duplicação de perguntas**: o split por grupo evita vazamento, mas perguntas repetidas (múltiplas respostas) reforçam o peso das classes populares.
- **Sem semântica profunda**: TF-IDF ignora contexto e ordem além de n-gramas; embeddings poderiam melhorar as classes minoritárias.

## 9. Contrato do modelo serializado

- `models/intent_classifier.joblib`: `Pipeline` sklearn que aceita `list[str]` em `.predict`/`.predict_proba` e expõe `.classes_`.
- Ordem de `classes_`: `[np.str_('Anatomia e fisiologia'), np.str_('Diagnóstico'), np.str_('Epidemiologia'), np.str_('Escolha de profissionais de saúde'), np.str_('Estilo de vida saudável'), np.str_('Outros'), np.str_('Tratamento')]`.
- `models/manifest.json`: metadados com o `sha256` real do `.joblib`, `sklearn_version=1.9.1`, hiperparâmetros e métricas.
