"""Configuração do banco de dados (SQLModel) e sessão por requisição."""
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import DATABASE_URL

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)


def init_db() -> None:
    """Cria as tabelas do banco de dados, se ainda não existirem."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Fornece uma sessão de banco de dados por requisição (dependency do FastAPI)."""
    with Session(engine) as session:
        yield session
