"""Entry point da HealthAssist API."""
import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import CORS_ORIGINS
from app.db import init_db
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.rate_limit import limiter
from app.routes import auth, health, predict, triagens

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HealthAssist API", version="0.1.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # allowlist explícita, nunca "*" (OWASP Top 10)
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health.router, prefix="")
app.include_router(auth.router, prefix="/auth")
app.include_router(predict.router, prefix="")
app.include_router(triagens.router, prefix="")


@app.on_event("startup")
async def on_startup() -> None:
    """Inicializa o banco de dados e loga a inicialização da API."""
    init_db()
    logger.info("API iniciada")
