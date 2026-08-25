"""Rota de health check, sem autenticação."""
from datetime import datetime, timezone

from fastapi import APIRouter

from app import __version__
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Retorna o status atual da API."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        version=__version__,
    )
