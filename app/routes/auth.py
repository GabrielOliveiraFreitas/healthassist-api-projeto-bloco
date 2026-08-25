"""Rota de autenticação: emissão de token JWT."""
from fastapi import APIRouter, HTTPException, status

from app.config import TOKEN_EXPIRATION_HOURS
from app.models.schemas import TokenRequest, TokenResponse
from app.security.jwt_handler import create_access_token

router = APIRouter()

# Placeholder MVP: usuário fixo até integração com banco de dados.
_PLACEHOLDER_USERNAME = "admin"
_PLACEHOLDER_PASSWORD = "senha123"


@router.post("/token", response_model=TokenResponse)
async def login(credentials: TokenRequest) -> TokenResponse:
    """Valida credenciais e retorna um token de acesso JWT."""
    if credentials.username != _PLACEHOLDER_USERNAME or credentials.password != _PLACEHOLDER_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(data={"sub": credentials.username})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=TOKEN_EXPIRATION_HOURS * 3600,
    )
