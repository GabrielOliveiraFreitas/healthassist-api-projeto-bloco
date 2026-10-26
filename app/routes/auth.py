"""Rota de autenticação: emissão de token JWT."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.config import RATE_LIMIT_AUTH, TOKEN_EXPIRATION_HOURS
from app.db import get_session
from app.models.entities import User
from app.models.schemas import TokenRequest, TokenResponse
from app.rate_limit import limiter
from app.security.jwt_handler import create_access_token
from app.security.passwords import DUMMY_HASH, verify_password

router = APIRouter()


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Obter token JWT",
    responses={
        401: {"description": "Credenciais inválidas"},
        422: {"description": "Body inválido (campo ausente, extra ou grande demais)"},
        429: {"description": "Limite de tentativas excedido (RATE_LIMIT_AUTH, por IP)"},
    },
)
@limiter.limit(RATE_LIMIT_AUTH)
async def login(
    request: Request,
    credentials: TokenRequest,
    session: Session = Depends(get_session),
) -> TokenResponse:
    """Valida credenciais contra a tabela de usuários e retorna um JWT.

    A senha é conferida contra o hash scrypt em tempo constante; para usuário
    inexistente é feita uma verificação fictícia, de modo que a resposta não
    revele (por conteúdo ou timing) se o username existe. Limitado por IP.
    """
    user = session.exec(select(User).where(User.username == credentials.username)).first()
    password_ok = verify_password(credentials.password, user.password_hash if user else DUMMY_HASH)

    if user is None or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(data={"sub": user.username})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=TOKEN_EXPIRATION_HOURS * 3600,
    )
