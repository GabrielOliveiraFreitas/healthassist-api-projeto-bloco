"""Entidades SQLModel (tabelas do banco de dados)."""
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Triagem(SQLModel, table=True):
    """Registro de uma triagem realizada via /predict, vinculado ao usuário dono."""

    id: Optional[int] = Field(default=None, primary_key=True)
    owner: str = Field(index=True)
    symptoms: List[str] = Field(sa_column=Column(JSON))
    prediction: str
    confidence: float
    recommendation: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class User(SQLModel, table=True):
    """Usuário da API. Guarda apenas o hash da senha (scrypt), nunca a senha."""

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
