"""Carregamento e uso do classificador de intenções (TF-IDF + LogisticRegression).

O artefato é um Pipeline scikit-learn treinado em ``eda/classificacao_tp4.py`` e
versionado em ``models/``. Nunca desserialize artefatos enviados pelo usuário: só o
arquivo local confiável é carregado, e ainda assim a integridade é checada por SHA-256
e a versão do scikit-learn é validada contra o manifest (evita desserialização
incompatível, CWE-502).
"""
import hashlib
import io
import json
from functools import lru_cache
from pathlib import Path
from typing import Tuple

import joblib
import sklearn

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_PATH = MODEL_DIR / "intent_classifier.joblib"
MANIFEST_PATH = MODEL_DIR / "manifest.json"


class ClassifierUnavailable(RuntimeError):
    """Modelo ausente, corrompido ou incompatível com o ambiente."""


@lru_cache(maxsize=1)
def load_classifier() -> Tuple[object, dict]:
    """Carrega o Pipeline treinado validando integridade (SHA-256) e versão do sklearn.

    Levanta ``ClassifierUnavailable`` em qualquer inconsistência, para que a rota
    responda 503 em vez de servir um modelo não confiável.
    """
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        raw = MODEL_PATH.read_bytes()
    except OSError as exc:
        raise ClassifierUnavailable("Artefato do modelo ausente") from exc

    if hashlib.sha256(raw).hexdigest() != manifest.get("sha256"):
        raise ClassifierUnavailable("Falha na checagem de integridade do modelo")
    if sklearn.__version__ != manifest.get("sklearn_version"):
        raise ClassifierUnavailable(
            f"Versão do scikit-learn incompatível: ambiente {sklearn.__version__} "
            f"!= manifest {manifest.get('sklearn_version')}"
        )

    model = joblib.load(io.BytesIO(raw))
    if list(getattr(model, "classes_", [])) != manifest.get("classes"):
        raise ClassifierUnavailable("Rótulos do modelo divergem do manifest")
    return model, manifest


def classify_text(text: str) -> dict:
    """Classifica a intenção de um texto, retornando intent, probabilidade e versão."""
    model, manifest = load_classifier()
    proba = model.predict_proba([text])[0]
    index = int(proba.argmax())
    return {
        "intent": str(model.classes_[index]),
        "probability": float(proba[index]),
        "model_version": manifest["version"],
    }
