"""Testes de segurança pedidos no TP2: sem token, BOLA e campo extra no body."""
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.config import RATE_LIMIT_AUTH
from app.models.entities import Triagem
from app.security.jwt_handler import create_access_token


def _auth_header(username: str) -> dict[str, str]:
    token = create_access_token(data={"sub": username})
    return {"Authorization": f"Bearer {token}"}


def test_predict_sem_token_retorna_401(client: TestClient) -> None:
    """(a) Chamar /predict sem token deve retornar 401."""
    response = client.post("/predict", json={"symptoms": ["febre"]})

    assert response.status_code == 401


def test_bola_nao_acessa_triagem_de_outro_usuario(client: TestClient, session: Session) -> None:
    """(b) Usuário B não pode ler uma triagem que pertence ao usuário A (BOLA)."""
    triagem_de_alice = Triagem(
        owner="alice",
        symptoms=["febre", "tosse"],
        prediction="placeholder",
        confidence=0.0,
        recommendation="Aguarde integração com modelo de EDA",
    )
    session.add(triagem_de_alice)
    session.commit()
    session.refresh(triagem_de_alice)

    resposta_bob = client.get(f"/triagens/{triagem_de_alice.id}", headers=_auth_header("bob"))
    assert resposta_bob.status_code == 404

    resposta_alice = client.get(f"/triagens/{triagem_de_alice.id}", headers=_auth_header("alice"))
    assert resposta_alice.status_code == 200
    assert resposta_alice.json()["owner"] == "alice"


def test_campo_extra_no_body_e_rejeitado(client: TestClient) -> None:
    """(c) Campo não esperado no body de /predict deve ser rejeitado (422, extra="forbid")."""
    response = client.post(
        "/predict",
        json={"symptoms": ["febre"], "campo_nao_esperado": "valor"},
        headers=_auth_header("admin"),
    )

    assert response.status_code == 422


def test_rate_limit_em_auth_token(client: TestClient) -> None:
    """(bônus) Após estourar o limite configurado, /auth/token deve retornar 429."""
    limite = int(RATE_LIMIT_AUTH.split("/")[0])
    payload = {"username": "admin", "password": "senha-errada"}

    for _ in range(limite):
        client.post("/auth/token", json=payload)

    resposta_excedente = client.post("/auth/token", json=payload)
    assert resposta_excedente.status_code == 429
