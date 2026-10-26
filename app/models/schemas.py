"""Modelos Pydantic usados pelas rotas da API."""
from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class TokenRequest(BaseModel):
    # extra="forbid" (OWASP): rejeita campos não esperados no body (422).
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=64, examples=["alice"])
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symptoms: List[Annotated[str, Field(min_length=1, max_length=100)]] = Field(
        min_length=1, max_length=20, examples=[["febre", "tosse"]]
    )


class PredictResponse(BaseModel):
    id: int
    prediction: str
    confidence: float
    recommendation: str


class TriagemResponse(BaseModel):
    id: int
    owner: str
    symptoms: List[str]
    prediction: str
    confidence: float
    recommendation: str
    created_at: datetime
