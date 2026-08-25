"""Rota de predição (placeholder), protegida por JWT."""
from fastapi import APIRouter, Depends

from app.models.schemas import PredictRequest, PredictResponse
from app.security.jwt_handler import get_current_user

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict(
    request: PredictRequest,
    current_user: str = Depends(get_current_user),
) -> PredictResponse:
    """Retorna uma predição placeholder até a integração com o modelo de EDA."""
    return PredictResponse(
        prediction="placeholder",
        confidence=0.0,
        recommendation="Aguarde integração com modelo de EDA",
    )
