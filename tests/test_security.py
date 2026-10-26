"""Testes de segurança: autenticação, autorização (BOLA), validação de entrada e rate limit."""
from datetime import timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.config import ALGORITHM, RATE_LIMIT_AUTH, SECRET_KEY
from app.models.entities import Triagem, User
from app.security.jwt_handler import create_access_token
from app.security.passwords import hash_password, verify_password

SENHA_ALICE = "senha-de-teste-alice"


def _auth_header(username: str) -> dict[str, str]:
    token = create_access_token(data={"sub": username})
    return {"Authorization": f"Bearer {token}"}


def _nova_triagem(session: Session, owner: str) -> Triagem:
    triagem = Triagem(
        owner=owner,
        symptoms=["febre", "tosse"],
        prediction="placeholder",
        confidence=0.0,
        recommendation="Aguarde integração com modelo de EDA",
    )
    session.add(triagem)
    session.commit()
    session.refresh(triagem)
    return triagem


# ---------------------------------------------------------------- autenticação
def test_predict_sem_token_retorna_401(client: TestClient) -> None:
    """Chamar /predict sem token deve retornar 401."""
    assert client.post("/predict", json={"symptoms": ["febre"]}).status_code == 401


def test_token_expirado_e_rejeitado(client: TestClient) -> None:
    """Token com `exp` no passado não dá acesso."""
    expirado = create_access_token({"sub": "alice"}, expires_delta=timedelta(seconds=-5))
    resp = client.post(
        "/predict", json={"symptoms": ["febre"]}, headers={"Authorization": f"Bearer {expirado}"}
    )
    assert resp.status_code == 401


def test_token_com_assinatura_invalida_e_rejeitado(client: TestClient) -> None:
    """Token assinado com outra chave (forjado) é rejeitado."""
    forjado = jwt.encode({"sub": "alice"}, "outra-chave-qualquer-0123456789abcdef", algorithm=ALGORITHM)
    resp = client.post(
        "/predict", json={"symptoms": ["febre"]}, headers={"Authorization": f"Bearer {forjado}"}
    )
    assert resp.status_code == 401


def test_token_alg_none_e_rejeitado(client: TestClient) -> None:
    """Token não assinado (alg=none) não é aceito."""
    sem_assinatura = jwt.encode({"sub": "alice"}, key=None, algorithm="none")
    resp = client.post(
        "/predict",
        json={"symptoms": ["febre"]},
        headers={"Authorization": f"Bearer {sem_assinatura}"},
    )
    assert resp.status_code == 401


def test_login_valido_e_invalido(client: TestClient, session: Session) -> None:
    """Login lê o usuário do banco; senha errada e usuário inexistente dão o mesmo 401."""
    session.add(User(username="alice", password_hash=hash_password(SENHA_ALICE)))
    session.commit()

    ok = client.post("/auth/token", json={"username": "alice", "password": SENHA_ALICE})
    assert ok.status_code == 200
    assert jwt.decode(ok.json()["access_token"], SECRET_KEY, algorithms=[ALGORITHM])["sub"] == "alice"

    senha_errada = client.post("/auth/token", json={"username": "alice", "password": "errada"})
    inexistente = client.post("/auth/token", json={"username": "ninguem", "password": "x"})
    assert senha_errada.status_code == inexistente.status_code == 401
    assert senha_errada.json() == inexistente.json()


def test_senha_nao_e_armazenada_em_texto_puro() -> None:
    """O hash não contém a senha, é salgado e verifica corretamente."""
    h1, h2 = hash_password(SENHA_ALICE), hash_password(SENHA_ALICE)
    assert SENHA_ALICE not in h1
    assert h1 != h2
    assert verify_password(SENHA_ALICE, h1)
    assert not verify_password("outra", h1)


# ------------------------------------------------------------- autorização/BOLA
def test_bola_nao_acessa_triagem_de_outro_usuario(client: TestClient, session: Session) -> None:
    """Usuário B não lê triagem de A; recebe o mesmo 404 de um id inexistente."""
    triagem = _nova_triagem(session, "alice")

    bob = client.get(f"/triagens/{triagem.id}", headers=_auth_header("bob"))
    inexistente = client.get("/triagens/99999", headers=_auth_header("bob"))
    assert bob.status_code == inexistente.status_code == 404
    assert bob.json() == inexistente.json()

    alice = client.get(f"/triagens/{triagem.id}", headers=_auth_header("alice"))
    assert alice.status_code == 200
    assert alice.json()["owner"] == "alice"


def test_triagens_sem_token_retorna_401(client: TestClient, session: Session) -> None:
    """GET /triagens/{id} exige autenticação."""
    triagem = _nova_triagem(session, "alice")
    assert client.get(f"/triagens/{triagem.id}").status_code == 401


# ------------------------------------------------------------ validação de entrada
def test_campo_extra_no_body_e_rejeitado(client: TestClient) -> None:
    """Campo não esperado no body de /predict é rejeitado (422, extra="forbid")."""
    resp = client.post(
        "/predict",
        json={"symptoms": ["febre"], "campo_nao_esperado": "valor"},
        headers=_auth_header("admin"),
    )
    assert resp.status_code == 422


@pytest.mark.parametrize(
    "corpo",
    [
        {"symptoms": []},
        {"symptoms": [""]},
        {"symptoms": ["x" * 101]},
        {"symptoms": ["febre"] * 21},
        {"symptoms": "febre"},
        {"symptoms": [1, 2]},
        {},
    ],
)
def test_predict_valida_formato_e_tamanho(client: TestClient, corpo: dict) -> None:
    """Listas vazias/enormes e tipos errados são barrados antes de chegar ao banco."""
    resp = client.post("/predict", json=corpo, headers=_auth_header("admin"))
    assert resp.status_code == 422


def test_predict_com_payload_de_sql_injection_e_tratado_como_dado(
    client: TestClient, session: Session
) -> None:
    """Tentativa de SQLi vira texto inerte (queries parametrizadas); a tabela segue íntegra."""
    payload = "'; DROP TABLE triagem; --"
    resp = client.post("/predict", json={"symptoms": [payload]}, headers=_auth_header("alice"))
    assert resp.status_code == 200
    salvo = client.get(f"/triagens/{resp.json()['id']}", headers=_auth_header("alice"))
    assert salvo.json()["symptoms"] == [payload]


def test_login_rejeita_campo_extra(client: TestClient) -> None:
    """/auth/token também usa extra="forbid"."""
    resp = client.post("/auth/token", json={"username": "a", "password": "b", "is_admin": True})
    assert resp.status_code == 422


# --------------------------------------------------------- headers / rate limiting
def test_headers_de_seguranca_presentes(client: TestClient) -> None:
    """Respostas trazem HSTS, X-Frame-Options, nosniff e CSP."""
    headers = client.get("/health").headers
    assert "max-age" in headers["strict-transport-security"]
    assert headers["x-frame-options"] == "DENY"
    assert headers["x-content-type-options"] == "nosniff"
    assert "default-src" in headers["content-security-policy"]


def test_cors_nao_libera_origem_fora_da_allowlist(client: TestClient) -> None:
    """Origem não listada não recebe Access-Control-Allow-Origin."""
    resp = client.get("/health", headers={"Origin": "https://malicioso.example"})
    assert "access-control-allow-origin" not in resp.headers


def test_rate_limit_em_auth_token(client: TestClient) -> None:
    """Após estourar o limite configurado, /auth/token deve retornar 429."""
    limite = int(RATE_LIMIT_AUTH.split("/")[0])
    payload = {"username": "admin", "password": "senha-errada"}

    for _ in range(limite):
        assert client.post("/auth/token", json=payload).status_code == 401

    assert client.post("/auth/token", json=payload).status_code == 429
