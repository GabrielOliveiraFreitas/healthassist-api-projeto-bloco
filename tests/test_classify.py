"""Testes do endpoint POST /classify (classificação de intenção, protegido por JWT)."""
import json

import pytest
from fastapi.testclient import TestClient

from app.classifier import MANIFEST_PATH, MODEL_PATH
from app.security.jwt_handler import create_access_token

_MODEL_PRESENTE = MODEL_PATH.exists() and MANIFEST_PATH.exists()
_skip_sem_modelo = pytest.mark.skipif(
    not _MODEL_PRESENTE, reason="modelo intent_classifier.joblib ainda não treinado"
)


def _auth_header(username: str = "alice") -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token({'sub': username})}"}


def test_classify_sem_token_retorna_401(client: TestClient) -> None:
    """Sem Bearer, /classify deve negar com 401."""
    assert client.post("/classify", json={"text": "dor no joelho"}).status_code == 401


def test_classify_rejeita_campo_extra_422(client: TestClient) -> None:
    """extra='forbid': campo não previsto no body é rejeitado antes de tocar no modelo."""
    resp = client.post(
        "/classify",
        json={"text": "dor no joelho", "owner": "bob"},
        headers=_auth_header(),
    )
    assert resp.status_code == 422


def test_classify_texto_vazio_422(client: TestClient) -> None:
    """Texto vazio viola min_length=1 e retorna 422."""
    resp = client.post("/classify", json={"text": ""}, headers=_auth_header())
    assert resp.status_code == 422


@_skip_sem_modelo
def test_classify_retorna_intencao_valida(client: TestClient) -> None:
    """Com token e texto válido, retorna uma intenção conhecida e probabilidade em [0,1]."""
    classes = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["classes"]
    resp = client.post(
        "/classify",
        json={"text": "Qual o melhor tratamento para capsulite adesiva no ombro?"},
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["intent"] in classes
    assert 0.0 <= body["probability"] <= 1.0
    assert body["model_version"]
