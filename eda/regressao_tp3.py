"""Regressão linear reprodutível (TP3) — dataset MedPT.

Versão em script do notebook `regressao_medpt.ipynb`, para execução não
interativa e reprodutível. Replica exatamente a mesma análise:

    (a) pré-processamento   -> variáveis derivadas + StandardScaler + OneHotEncoder
    (b) regressão múltipla  -> 3 features numéricas + question_type (one-hot)
    (c) métricas            -> R² e RMSE (modelo simples e múltiplo)
    (d) residual plot       -> eda/residual_plot.png
    (e) Q-Q plot            -> eda/qq_plot.png
    (f) limitações          -> impressas ao final e documentadas no notebook

Uso:
    <REPO>/.venv/bin/python eda/regressao_tp3.py        # se o venv tiver as libs
    # senão, um venv com pandas/scikit-learn/scipy/matplotlib:
    python3 eda/regressao_tp3.py

Dependências: pandas, numpy, scikit-learn, scipy, matplotlib.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # backend sem display, para rodar em servidor/CI
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

AQUI = Path(__file__).resolve().parent
CSV = AQUI / "medpt_amostra.csv"
RANDOM_STATE = 42


def carregar_dados() -> pd.DataFrame:
    """Lê a amostra do MedPT e cria as variáveis derivadas (pré-processamento)."""
    df = pd.read_csv(CSV)
    df["tam_pergunta"] = df["question"].str.split().str.len()
    df["tam_resposta"] = df["answer"].astype(str).str.split().str.len()
    df["palavras_unicas"] = df["question"].apply(lambda x: len(set(str(x).lower().split())))
    df["num_interrogacoes"] = df["question"].str.count(r"\?")
    return df


def separar_treino_teste(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split agrupado pela pergunta (GroupShuffleSplit), evitando vazamento.

    Cada pergunta aparece em várias linhas (uma por resposta de médico). Separar
    por linha vazaria o mesmo texto entre treino e teste e inflaria o resultado.
    """
    splitter = GroupShuffleSplit(test_size=0.2, random_state=RANDOM_STATE)
    idx_treino, idx_teste = next(splitter.split(df, df["tam_resposta"], df["question"]))
    return df.iloc[idx_treino], df.iloc[idx_teste]


def regressao_simples(treino: pd.DataFrame, teste: pd.DataFrame) -> tuple[float, float, np.ndarray]:
    """Regressão linear simples usando apenas `tam_pergunta`."""
    modelo = Pipeline([("escala", StandardScaler()), ("modelo", LinearRegression())])
    modelo.fit(treino[["tam_pergunta"]], treino["tam_resposta"])
    pred = modelo.predict(teste[["tam_pergunta"]])
    r2 = r2_score(teste["tam_resposta"], pred)
    rmse = mean_squared_error(teste["tam_resposta"], pred) ** 0.5
    return r2, rmse, pred


def regressao_multipla(treino: pd.DataFrame, teste: pd.DataFrame) -> tuple[float, float, np.ndarray]:
    """Regressão linear MÚLTIPLA: 3 features numéricas + question_type (one-hot)."""
    numericas = ["tam_pergunta", "palavras_unicas", "num_interrogacoes"]
    categoricas = ["question_type"]
    pre = ColumnTransformer(
        [
            ("num", StandardScaler(), numericas),
            ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), categoricas),
        ]
    )
    modelo = Pipeline([("pre", pre), ("modelo", LinearRegression())])
    modelo.fit(treino[numericas + categoricas], treino["tam_resposta"])
    pred = modelo.predict(teste[numericas + categoricas])
    r2 = r2_score(teste["tam_resposta"], pred)
    rmse = mean_squared_error(teste["tam_resposta"], pred) ** 0.5
    return r2, rmse, pred


def gerar_graficos(teste: pd.DataFrame, pred_mult: np.ndarray) -> float:
    """Gera residual plot e Q-Q plot a partir dos resíduos do modelo múltiplo."""
    residuos = teste["tam_resposta"].values - pred_mult

    plt.figure(figsize=(7, 5))
    plt.scatter(pred_mult, residuos, alpha=0.3, s=15)
    plt.axhline(0, color="red")
    plt.xlabel("Valor previsto")
    plt.ylabel("Resíduo")
    plt.title("Residual plot")
    plt.tight_layout()
    plt.savefig(AQUI / "residual_plot.png")
    plt.close()

    plt.figure(figsize=(6, 6))
    stats.probplot(residuos, dist="norm", plot=plt)
    plt.title("Q-Q plot dos resíduos")
    plt.tight_layout()
    plt.savefig(AQUI / "qq_plot.png")
    plt.close()

    return float(stats.skew(residuos))


def main() -> None:
    df = carregar_dados()
    treino, teste = separar_treino_teste(df)
    print(f"linhas: {df.shape[0]} | treino: {len(treino)} | teste: {len(teste)}")

    r2_s, rmse_s, _ = regressao_simples(treino, teste)
    r2_m, rmse_m, pred_mult = regressao_multipla(treino, teste)

    print("\n=== Métricas ===")
    print(f"simples  -> R2={r2_s:.4f}  RMSE={rmse_s:.2f}")
    print(f"múltipla -> R2={r2_m:.4f}  RMSE={rmse_m:.2f}")

    skew = gerar_graficos(teste, pred_mult)
    print(f"\nassimetria (skew) dos resíduos: {skew:.2f}")
    print("PNGs gerados: residual_plot.png, qq_plot.png")

    print("\n=== Limitações ===")
    print(
        "- R² ~0: o tamanho da pergunta quase não explica o da resposta "
        "(correlação ~0,09 no TP2).\n"
        "- Resíduos assimétricos (skew ~2) e com cauda longa: violam a "
        "normalidade/homocedasticidade assumidas pela regressão linear.\n"
        "- A tarefa real do projeto é CLASSIFICAÇÃO de intenção, não regressão; "
        "este exercício apenas evidencia a inadequação do modelo linear aqui."
    )


if __name__ == "__main__":
    main()
