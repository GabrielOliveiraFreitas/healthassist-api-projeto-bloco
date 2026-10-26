"""Testes unitários: JWT, hashing, config, seed e rotas básicas."""
import importlib
import time
from datetime import timedelta

import jwt
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session, select

import app.config as config
from app.models.entities import Triagem, User
from app.security import jwt_handler
from app.security.passwords import hash_password, verify_password


# ------------------------------------------------------------------- JWT
def test_create_e_verify_token_roundtrip() -> None:
    token = jwt_handler.create_access_token({"sub": "alice"})
    assert jwt_handler.verify_token(token)["sub"] == "alice"


def test_token_tem_expiracao_padrao_de_uma_hora() -> None:
    payload = jwt_handler.verify_token(jwt_handler.create_access_token({"sub": "a"}))
    restante = payload["exp"] - time.time()
    assert 3500 < restante <= 3600


def test_verify_token_lixo_levanta_401() -> None:
    with pytest.raises(HTTPException) as exc:
        jwt_handler.verify_token("isto.nao.e-jwt")
    assert exc.value.status_code == 401


def test_get_current_user_sem_sub_levanta_401() -> None:
    token = jwt.encode({"x": 1}, config.SECRET_KEY, algorithm=config.ALGORITHM)
    with pytest.raises(HTTPException) as exc:
        jwt_handler.get_current_user(token)
    assert exc.value.status_code == 401


def test_token_expirado_levanta_401() -> None:
    token = jwt_handler.create_access_token({"sub": "a"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(HTTPException):
        jwt_handler.verify_token(token)


# ------------------------------------------------------------- senhas
def test_verify_password_rejeita_hash_malformado() -> None:
    assert not verify_password("x", "lixo")
    assert not verify_password("x", "bcrypt$abc$def")
    assert not verify_password("x", "scrypt$%%%$%%%")


def test_hashes_diferentes_para_mesma_senha() -> None:
    assert hash_password("mesma-senha") != hash_password("mesma-senha")


# ------------------------------------------------------------- config
def test_config_recusa_secret_key_ausente_ou_curta(monkeypatch: pytest.MonkeyPatch) -> None:
    original = config.SECRET_KEY
    try:
        for valor in ("", "curta"):
            monkeypatch.setenv("SECRET_KEY", valor)
            with pytest.raises(RuntimeError):
                importlib.reload(config)
    finally:
        monkeypatch.setenv("SECRET_KEY", original)
        importlib.reload(config)


def test_cors_origins_nunca_e_wildcard() -> None:
    assert "*" not in config.CORS_ORIGINS


# --------------------------------------------------------------- rotas
def test_health_responde_sem_autenticacao(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_predict_persiste_triagem_do_usuario(client: TestClient, session: Session) -> None:
    token = jwt_handler.create_access_token({"sub": "alice"})
    resp = client.post(
        "/predict", json={"symptoms": ["febre"]}, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    salvo = session.exec(select(Triagem).where(Triagem.id == resp.json()["id"])).one()
    assert salvo.owner == "alice"


def test_metodo_nao_permitido_retorna_405(client: TestClient) -> None:
    assert client.delete("/health").status_code == 405
    assert client.get("/auth/token").status_code == 405


# ---------------------------------------------------------------- seed
def test_seed_cria_usuarios_com_hash_e_e_idempotente(
    monkeypatch: pytest.MonkeyPatch, session: Session
) -> None:
    import scripts.seed as seed

    monkeypatch.setattr(seed, "engine", session.get_bind())
    monkeypatch.setattr(seed, "init_db", lambda: None)
    for u in seed.SEED_USERS:
        monkeypatch.setenv(f"SEED_{u.upper()}_PASSWORD", f"senha-{u}-123")

    assert seed.main() == 0
    assert seed.main() == 0  # idempotente
    usuarios = session.exec(select(User)).all()
    assert {u.username for u in usuarios} == set(seed.SEED_USERS)
    assert all("senha-" not in u.password_hash for u in usuarios)


def test_seed_falha_sem_senhas(monkeypatch: pytest.MonkeyPatch) -> None:
    import scripts.seed as seed

    for u in seed.SEED_USERS:
        monkeypatch.delenv(f"SEED_{u.upper()}_PASSWORD", raising=False)
    assert seed.main() == 1
