"""Rota de predição (placeholder), protegida por JWT."""
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db import get_session
from app.models.entities import Triagem
from app.models.schemas import PredictRequest, PredictResponse
from app.security.jwt_handler import get_current_user

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict(
    request: PredictRequest,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> PredictResponse:
    """Gera uma predição placeholder e persiste a triagem vinculada ao usuário autenticado."""
    triagem = Triagem(
        owner=current_user,
        symptoms=request.symptoms,
        prediction="placeholder",
        confidence=0.0,
        recommendation="Aguarde integração com modelo de EDA",
    )
    session.add(triagem)
    session.commit()
    session.refresh(triagem)

    return PredictResponse(
        id=triagem.id,
        prediction=triagem.prediction,
        confidence=triagem.confidence,
        recommendation=triagem.recommendation,
    )
