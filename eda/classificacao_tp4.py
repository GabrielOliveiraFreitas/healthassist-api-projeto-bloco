"""Classificação de Intenções (question_type) — TP4 HealthAssist.

Pipeline reprodutível de classificação multiclasse de intenção médica em
português: prevê ``question_type`` (7 classes) a partir do texto ``question``.

Etapas:
    1. Carregamento e inspeção do dataset (eda/medpt_amostra.csv).
    2. Pré-processamento de texto + TF-IDF + Regressão Logística (multinomial).
    3. Split sem vazamento por pergunta (GroupShuffleSplit, groups=question).
    4. GridSearchCV (f1_macro) sobre >=2 hiperparâmetros com >=3 valores cada.
    5. Avaliação: classification_report, F1-macro, acurácia, matriz de confusão.
    6. Baseline (DummyClassifier most_frequent) para comparação honesta.
    7. Re-treino no dataset inteiro e serialização (joblib) + manifest.json.

Execução:
    python eda/classificacao_tp4.py

O backend do matplotlib é forçado para 'Agg' (sem display).
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # backend não interativo (salva em arquivo)

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import GridSearchCV, GroupShuffleSplit, StratifiedGroupKFold
from sklearn.pipeline import Pipeline

import joblib

# --------------------------------------------------------------------------- #
# Caminhos
# --------------------------------------------------------------------------- #
REPO = Path(__file__).resolve().parents[1]
EDA = REPO / "eda"
MODELS = REPO / "models"
DATASET = EDA / "medpt_amostra.csv"
MODEL_PATH = MODELS / "intent_classifier.joblib"
MANIFEST_PATH = MODELS / "manifest.json"
CONFUSION_PNG = EDA / "matriz_confusao.png"
REPORT_PATH = EDA / "classificacao_relatorio.md"

RANDOM_STATE = 42
MODEL_VERSION = "healthassist-intents-tp4-v1"
SKLEARN_VERSION = "1.9.1"

# Stopwords em português (lista enxuta; TF-IDF também usa min_df para ruído).
STOPWORDS_PT = [
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos",
    "das", "em", "no", "na", "nos", "nas", "por", "para", "com", "sem", "sob",
    "sobre", "e", "ou", "mas", "que", "se", "ao", "aos", "à", "às", "pelo",
    "pela", "pelos", "pelas", "este", "esta", "isto", "esse", "essa", "isso",
    "aquele", "aquela", "aquilo", "meu", "minha", "seu", "sua", "eu", "ele",
    "ela", "nos", "voce", "vocês", "me", "te", "lhe", "ser", "estar", "ter",
    "haver", "foi", "era", "é", "são", "está", "estão", "muito", "muita",
    "mais", "menos", "ja", "já", "nao", "não", "sim", "tambem", "também",
    "como", "quando", "onde", "porque", "qual", "quais", "quem",
]


# --------------------------------------------------------------------------- #
# Pré-processamento de texto
# --------------------------------------------------------------------------- #
def preprocessar_texto(texto: str) -> str:
    """Normaliza uma pergunta em português para vetorização.

    Aplica: minúsculas, remoção de acentos (NFKD), substituição de qualquer
    caractere não alfabético por espaço e colapso de espaços. Mantém o texto
    cru interpretável pelo TfidfVectorizer (que ainda tokeniza/ngrama).

    Args:
        texto: a pergunta original.

    Returns:
        o texto normalizado.
    """
    if not isinstance(texto, str):
        texto = str(texto)
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-zç\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


# Stopwords também precisam ser normalizadas (sem acento) para casar com o texto.
STOPWORDS_PT_NORM = sorted(
    {preprocessar_texto(w) for w in STOPWORDS_PT if preprocessar_texto(w)}
)


def construir_pipeline() -> Pipeline:
    """Monta o Pipeline TF-IDF -> LogisticRegression.

    O TfidfVectorizer é a PRIMEIRA etapa e recebe ``list[str]`` de texto cru.
    O pré-processamento equivalente ao de ``preprocessar_texto`` é feito com
    parâmetros NATIVOS do vetorizador (``lowercase=True``,
    ``strip_accents="unicode"`` e um ``token_pattern`` que mantém apenas
    tokens alfabéticos de 2+ letras). Isso é PROPOSITAL: evita gravar uma
    referência a função Python no ``.joblib``, deixando o modelo
    autossuficiente — o endpoint ``/classify`` só precisa do scikit-learn
    instalado para carregá-lo. A LogisticRegression é multinomial (default do
    lbfgs) com ``class_weight="balanced"`` para o forte desbalanceamento.
    Expõe ``predict_proba``.

    Returns:
        o Pipeline sklearn pronto para fit.
    """
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    token_pattern=r"(?u)\b[a-zA-Z]{2,}\b",
                    stop_words=STOPWORDS_PT_NORM,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def main() -> None:
    """Executa o pipeline completo e grava todos os entregáveis."""
    MODELS.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------------------------- #
    # 1. Carregamento
    # ----------------------------------------------------------------- #
    df = pd.read_csv(DATASET)
    df = df.dropna(subset=["question", "question_type"]).copy()
    X = df["question"].astype(str).tolist()
    y = df["question_type"].astype(str).tolist()
    groups = df["question"].astype(str).tolist()  # agrupa por pergunta

    print(f"[dados] {len(df)} linhas | {df['question'].nunique()} perguntas únicas")
    print("[dados] distribuição de question_type (linhas):")
    print(df["question_type"].value_counts().to_string())

    # ----------------------------------------------------------------- #
    # 2. Split sem vazamento (mesma pergunta não cai em treino e teste)
    # ----------------------------------------------------------------- #
    gss = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=RANDOM_STATE)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))
    X_train = [X[i] for i in train_idx]
    y_train = [y[i] for i in train_idx]
    g_train = [groups[i] for i in train_idx]
    X_test = [X[i] for i in test_idx]
    y_test = [y[i] for i in test_idx]

    # garantia: nenhuma pergunta compartilhada entre treino e teste
    overlap = set(X_train) & set(X_test)
    assert not overlap, f"vazamento: {len(overlap)} perguntas em comum"
    print(f"\n[split] treino={len(X_train)} teste={len(X_test)} (sem vazamento)")

    # ----------------------------------------------------------------- #
    # 3. GridSearchCV (f1_macro) com CV agrupada e estratificada
    # ----------------------------------------------------------------- #
    pipeline = construir_pipeline()
    param_grid = {
        "tfidf__ngram_range": [(1, 1), (1, 2), (1, 3)],
        "tfidf__min_df": [1, 2, 3],
        "clf__C": [0.1, 1.0, 10.0],
    }
    cv = StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=RANDOM_STATE)
    grid = GridSearchCV(
        pipeline,
        param_grid=param_grid,
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        verbose=1,
        refit=True,
    )
    grid.fit(X_train, y_train, groups=g_train)

    best_params = grid.best_params_
    print(f"\n[grid] melhores params: {best_params}")
    print(f"[grid] melhor f1_macro (CV): {grid.best_score_:.4f}")

    # ----------------------------------------------------------------- #
    # 4. Avaliação no conjunto de teste
    # ----------------------------------------------------------------- #
    best_model = grid.best_estimator_
    y_pred = best_model.predict(X_test)
    labels_sorted = sorted(set(y))

    f1_macro = f1_score(y_test, y_pred, average="macro")
    accuracy = accuracy_score(y_test, y_pred)
    report_txt = classification_report(y_test, y_pred, digits=3, zero_division=0)
    report_dict = classification_report(
        y_test, y_pred, output_dict=True, zero_division=0
    )
    print("\n[avaliação] classification_report (teste):")
    print(report_txt)
    print(f"[avaliação] F1-macro = {f1_macro:.4f} | acurácia = {accuracy:.4f}")

    # ----------------------------------------------------------------- #
    # 5. Baseline (classe mais frequente)
    # ----------------------------------------------------------------- #
    dummy = DummyClassifier(strategy="most_frequent")
    dummy.fit(X_train, y_train)
    y_dummy = dummy.predict(X_test)
    baseline_f1 = f1_score(y_test, y_dummy, average="macro")
    baseline_acc = accuracy_score(y_test, y_dummy)
    print(
        f"[baseline] F1-macro = {baseline_f1:.4f} | acurácia = {baseline_acc:.4f} "
        f"(DummyClassifier most_frequent)"
    )

    # ----------------------------------------------------------------- #
    # 6. Matriz de confusão (PNG)
    # ----------------------------------------------------------------- #
    cm = confusion_matrix(y_test, y_pred, labels=labels_sorted)
    fig, ax = plt.subplots(figsize=(9, 8))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels_sorted)
    disp.plot(ax=ax, cmap="Blues", xticks_rotation=45, colorbar=True)
    ax.set_title("Matriz de Confusão — Intenção (question_type) — Teste")
    plt.tight_layout()
    fig.savefig(CONFUSION_PNG, dpi=130)
    plt.close(fig)
    print(f"\n[figura] matriz de confusão salva em {CONFUSION_PNG}")

    # ----------------------------------------------------------------- #
    # 7. Re-treino no dataset INTEIRO e serialização
    # ----------------------------------------------------------------- #
    final_model = construir_pipeline()
    final_model.set_params(**best_params)
    final_model.fit(X, y)
    joblib.dump(final_model, MODEL_PATH)
    classes = list(final_model.classes_)
    print(f"\n[modelo] treinado no dataset inteiro e salvo em {MODEL_PATH}")
    print(f"[modelo] classes_ = {classes}")

    # sha256 REAL do arquivo salvo
    sha256 = hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest()

    manifest = {
        "version": MODEL_VERSION,
        "sha256": sha256,
        "sklearn_version": SKLEARN_VERSION,
        "classes": classes,
        "best_params": {
            "tfidf__ngram_range": list(best_params["tfidf__ngram_range"]),
            "tfidf__min_df": best_params["tfidf__min_df"],
            "clf__C": best_params["clf__C"],
        },
        "metrics": {
            "f1_macro": round(float(f1_macro), 4),
            "accuracy": round(float(accuracy), 4),
            "baseline_f1_macro": round(float(baseline_f1), 4),
            "baseline_accuracy": round(float(baseline_acc), 4),
        },
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "language": "pt",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"[manifest] salvo em {MANIFEST_PATH}")

    # verifica que o sha256 do manifest bate com o arquivo
    check = hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest()
    assert check == manifest["sha256"], "sha256 do manifest não bate com o arquivo"
    print(f"[manifest] sha256 verificado: {check}")

    # sanity check do contrato: aceita list[str] e expõe predict_proba
    exemplo = ["Qual o melhor tratamento para dor no joelho?"]
    pred = final_model.predict(exemplo)
    proba = final_model.predict_proba(exemplo)
    print(f"[contrato] predict({exemplo!r}) -> {pred.tolist()}")
    print(f"[contrato] predict_proba shape = {proba.shape}")

    # ----------------------------------------------------------------- #
    # 8. Relatório em markdown (números reais)
    # ----------------------------------------------------------------- #
    _escrever_relatorio(
        df=df,
        best_params=best_params,
        best_cv_score=grid.best_score_,
        report_dict=report_dict,
        f1_macro=f1_macro,
        accuracy=accuracy,
        baseline_f1=baseline_f1,
        baseline_acc=baseline_acc,
        n_train=len(X_train),
        n_test=len(X_test),
        classes=classes,
        labels_sorted=labels_sorted,
    )
    print(f"[relatório] salvo em {REPORT_PATH}")
    print("\n[OK] pipeline concluído com sucesso.")


def _escrever_relatorio(
    *,
    df: pd.DataFrame,
    best_params: dict,
    best_cv_score: float,
    report_dict: dict,
    f1_macro: float,
    accuracy: float,
    baseline_f1: float,
    baseline_acc: float,
    n_train: int,
    n_test: int,
    classes: list[str],
    labels_sorted: list[str],
) -> None:
    """Gera o relatório markdown com métricas reais do experimento."""
    dist_rows = df["question_type"].value_counts()
    dist_uniq = df.drop_duplicates("question")["question_type"].value_counts()

    linhas = []
    linhas.append("# Classificação de Intenções (question_type) — TP4\n")
    linhas.append("## 1. Pergunta de modelagem\n")
    linhas.append(
        "Dado o texto livre de uma pergunta médica em português "
        "(coluna `question`), **qual é a intenção do usuário** "
        "(coluna `question_type`)? Trata-se de uma classificação "
        "multiclasse com **7 classes**.\n"
    )

    linhas.append("## 2. Classes e distribuição\n")
    linhas.append(
        f"Dataset: `eda/medpt_amostra.csv` — {len(df)} linhas, "
        f"{df['question'].nunique()} perguntas únicas "
        f"(cada pergunta aparece ~{len(df)/df['question'].nunique():.1f}x, "
        "pois há múltiplas respostas por pergunta).\n"
    )
    linhas.append("| Classe | Linhas | % linhas | Perguntas únicas |")
    linhas.append("|---|---:|---:|---:|")
    for cls in dist_rows.index:
        linhas.append(
            f"| {cls} | {dist_rows[cls]} | "
            f"{100*dist_rows[cls]/len(df):.1f}% | {dist_uniq.get(cls, 0)} |"
        )
    linhas.append("")
    linhas.append(
        "O conjunto é **fortemente desbalanceado**: _Tratamento_ e "
        "_Diagnóstico_ somam a grande maioria, enquanto _Anatomia e "
        "fisiologia_ tem apenas ~25 perguntas únicas.\n"
    )

    linhas.append("## 3. Pipeline\n")
    linhas.append(
        "- **Pré-processamento + Vetorização**: `TfidfVectorizer` recebe o "
        "texto cru e aplica, com parâmetros nativos, minúsculas "
        "(`lowercase=True`), remoção de acentos (`strip_accents=\"unicode\"`) "
        "e um `token_pattern` que mantém apenas tokens alfabéticos de 2+ "
        "letras, além de stopwords em português e `sublinear_tf=True`. Usar "
        "parâmetros nativos (em vez de uma função Python) deixa o `.joblib` "
        "**autossuficiente**: o endpoint `/classify` só precisa do "
        "scikit-learn para carregá-lo.\n"
        "- **Classificador**: `LogisticRegression` multinomial com "
        "`class_weight=\"balanced\"` (expõe `predict_proba`, requisito do "
        "contrato do endpoint `/classify`).\n"
        "- **Split sem vazamento**: `GroupShuffleSplit` com `groups=question` "
        f"(75/25) — treino={n_train}, teste={n_test}. A mesma pergunta nunca "
        "aparece em treino e teste.\n"
        "- **Validação cruzada**: `StratifiedGroupKFold(n_splits=4)` dentro do "
        "`GridSearchCV` (respeita grupos e estratifica por classe).\n"
    )

    linhas.append("## 4. GridSearchCV — melhores hiperparâmetros\n")
    linhas.append(
        "Busca em grade (`scoring=\"f1_macro\"`, 3×3×3 = 27 combinações × 4 "
        "folds):\n"
    )
    linhas.append("| Hiperparâmetro | Valores testados | Melhor |")
    linhas.append("|---|---|---|")
    linhas.append(
        f"| `tfidf__ngram_range` | (1,1), (1,2), (1,3) | "
        f"{tuple(best_params['tfidf__ngram_range'])} |"
    )
    linhas.append(
        f"| `tfidf__min_df` | 1, 2, 3 | {best_params['tfidf__min_df']} |"
    )
    linhas.append(f"| `clf__C` | 0.1, 1, 10 | {best_params['clf__C']} |")
    linhas.append("")
    linhas.append(
        f"Melhor **F1-macro na validação cruzada**: **{best_cv_score:.3f}**.\n"
    )

    linhas.append("## 5. Métricas por classe (conjunto de teste)\n")
    linhas.append("| Classe | Precisão | Recall | F1 | Suporte |")
    linhas.append("|---|---:|---:|---:|---:|")
    for cls in labels_sorted:
        m = report_dict.get(cls, {})
        linhas.append(
            f"| {cls} | {m.get('precision', 0):.3f} | "
            f"{m.get('recall', 0):.3f} | {m.get('f1-score', 0):.3f} | "
            f"{int(m.get('support', 0))} |"
        )
    linhas.append("")
    linhas.append(
        f"- **F1-macro**: **{f1_macro:.3f}**\n"
        f"- **Acurácia**: **{accuracy:.3f}**\n"
    )

    linhas.append("## 6. Comparação com baseline\n")
    linhas.append("| Modelo | F1-macro | Acurácia |")
    linhas.append("|---|---:|---:|")
    linhas.append(
        f"| Baseline (`DummyClassifier` most_frequent) | "
        f"{baseline_f1:.3f} | {baseline_acc:.3f} |"
    )
    linhas.append(
        f"| **TF-IDF + LogisticRegression** | **{f1_macro:.3f}** | "
        f"**{accuracy:.3f}** |"
    )
    linhas.append("")
    ganho = f1_macro - baseline_f1
    linhas.append(
        f"O modelo supera a baseline em **{ganho:.3f}** de F1-macro "
        f"({baseline_f1:.3f} → {f1_macro:.3f}). A baseline atinge acurácia "
        f"de {baseline_acc:.3f} apenas prevendo sempre a classe majoritária, "
        "mas seu F1-macro é baixíssimo — isso ilustra por que **a acurácia "
        "sozinha engana** num problema tão desbalanceado, e por que "
        "escolhemos F1-macro como métrica principal.\n"
    )

    linhas.append("## 7. Matriz de confusão\n")
    linhas.append(
        "Ver `eda/matriz_confusao.png` (contagens no conjunto de teste). As "
        "confusões concentram-se entre _Tratamento_ e _Diagnóstico_ (classes "
        "majoritárias e semanticamente próximas) e nas classes minoritárias, "
        "que têm pouquíssimos exemplos.\n"
    )

    linhas.append("## 8. Limitações\n")
    linhas.append(
        "- **Desbalanceamento severo**: _Anatomia e fisiologia_ tem ~25 "
        "perguntas únicas; o recall nessas classes é instável.\n"
        "- **Rótulos ruidosos**: a fronteira entre _Tratamento_, _Diagnóstico_ "
        "e _Outros_ é subjetiva; há sobreposição semântica real.\n"
        "- **Português informal**: erros de digitação, abreviações e gírias "
        "não são corrigidos; apenas normalização básica é aplicada.\n"
        "- **Duplicação de perguntas**: o split por grupo evita vazamento, "
        "mas perguntas repetidas (múltiplas respostas) reforçam o peso das "
        "classes populares.\n"
        "- **Sem semântica profunda**: TF-IDF ignora contexto e ordem além de "
        "n-gramas; embeddings poderiam melhorar as classes minoritárias.\n"
    )

    linhas.append("## 9. Contrato do modelo serializado\n")
    linhas.append(
        "- `models/intent_classifier.joblib`: `Pipeline` sklearn que aceita "
        "`list[str]` em `.predict`/`.predict_proba` e expõe `.classes_`.\n"
        f"- Ordem de `classes_`: `{classes}`.\n"
        "- `models/manifest.json`: metadados com o `sha256` real do `.joblib`, "
        "`sklearn_version=1.9.1`, hiperparâmetros e métricas.\n"
    )

    REPORT_PATH.write_text("\n".join(linhas), encoding="utf-8")


if __name__ == "__main__":
    main()
