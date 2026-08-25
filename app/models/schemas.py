"""Modelos Pydantic usados pelas rotas da API."""
from typing import List

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class PredictRequest(BaseModel):
    symptoms: List[str]


class PredictResponse(BaseModel):
    prediction: str
    confidence: float
    recommendation: str
