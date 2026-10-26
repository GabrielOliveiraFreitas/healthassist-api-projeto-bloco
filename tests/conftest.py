"""Fixtures compartilhadas: cliente de teste com banco SQLite em memória."""
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

# Chave só para testes; precisa existir antes de importar app.config.
if len(os.environ.get("SECRET_KEY", "")) < 32:
    os.environ["SECRET_KEY"] = "chave-somente-para-testes-0123456789abcdef"

import app.main as main_module
from app.db import get_session
from app.main import app
from app.rate_limit import limiter

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def _override_get_session() -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = _override_get_session
# Evita que o evento de startup mexa no banco de dados "real" (arquivo .db).
main_module.init_db = lambda: None


@pytest.fixture(autouse=True)
def _fresh_database() -> Generator[None, None, None]:
    """Recria as tabelas e reseta o rate limiter antes de cada teste."""
    SQLModel.metadata.create_all(test_engine)
    limiter.reset()
    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def session() -> Generator[Session, None, None]:
    with Session(test_engine) as db_session:
        yield db_session
