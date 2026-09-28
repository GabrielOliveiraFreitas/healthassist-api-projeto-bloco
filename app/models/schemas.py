"""Modelos Pydantic usados pelas rotas da API."""
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class TokenRequest(BaseModel):
    # extra="forbid" (OWASP): rejeita campos não esperados no body (422).
    model_config = ConfigDict(extra="forbid")

    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symptoms: List[str]


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
