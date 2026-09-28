"""Rota de consulta de triagens por ID, protegida por JWT e ownership (BOLA)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models.entities import Triagem
from app.models.schemas import TriagemResponse
from app.security.jwt_handler import get_current_user

router = APIRouter()


@router.get("/triagens/{triagem_id}", response_model=TriagemResponse)
async def get_triagem(
    triagem_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Triagem:
    """Retorna uma triagem pelo ID, apenas se pertencer ao usuário autenticado.

    A checagem de ownership (BOLA) é feita na própria query — filtrando por
    `id` e `owner` ao mesmo tempo — para que uma triagem de outro usuário
    resulte no mesmo 404 de "não existe", sem revelar que o ID é válido.
    """
    triagem = session.exec(
        select(Triagem).where(Triagem.id == triagem_id, Triagem.owner == current_user)
    ).first()

    if triagem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Triagem not found")

    return triagem
