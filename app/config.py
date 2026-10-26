"""Configuração da aplicação carregada a partir de variáveis de ambiente."""
import os

from dotenv import load_dotenv

load_dotenv()

# Sem valor padrão: uma chave previsível permitiria forjar JWTs. A aplicação
# recusa subir sem SECRET_KEY forte definida no ambiente (fail fast).
_MIN_SECRET_KEY_LENGTH = 32
SECRET_KEY: str = os.getenv("SECRET_KEY", "")
if len(SECRET_KEY) < _MIN_SECRET_KEY_LENGTH:
    raise RuntimeError(
        f"SECRET_KEY ausente ou curta (mínimo {_MIN_SECRET_KEY_LENGTH} caracteres). "
        'Gere uma com: python -c "import secrets; print(secrets.token_urlsafe(48))"'
    )
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
TOKEN_EXPIRATION_HOURS: int = int(os.getenv("TOKEN_EXPIRATION_HOURS", "1"))
DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./healthassist.db")

# Allowlist explícita de origens para CORS — nunca usar "*" (OWASP Top 10).
CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

# Limite de tentativas em /auth/token para mitigar brute force (slowapi).
RATE_LIMIT_AUTH: str = os.getenv("RATE_LIMIT_AUTH", "5/minute")
