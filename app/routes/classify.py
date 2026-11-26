"""Rota de classificação de intenção, protegida por JWT."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.classifier import ClassifierUnavailable, classify_text
from app.models.schemas import ClassifyRequest, ClassifyResponse
from app.security.jwt_handler import get_current_user

router = APIRouter()


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    summary="Classificar a intenção de um texto de triagem",
    responses={
        401: {"description": "Bearer ausente ou inválido"},
        422: {"description": "Texto inválido ou campo extra"},
        503: {"description": "Classificador indisponível ou com integridade inválida"},
    },
)
async def classify(
    request: ClassifyRequest,
    current_user: str = Depends(get_current_user),
) -> ClassifyResponse:
    """Recebe um texto, autentica via JWT e retorna a intenção prevista + probabilidade."""
    try:
        result = classify_text(request.text)
    except ClassifierUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Classificador indisponível",
        ) from exc
    return ClassifyResponse(**result)
