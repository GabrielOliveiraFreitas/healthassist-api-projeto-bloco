"""Entry point da HealthAssist API."""
import logging

from dotenv import load_dotenv
from fastapi import FastAPI

from app.routes import auth, health, predict

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HealthAssist API", version="0.1.0")

app.include_router(health.router, prefix="")
app.include_router(auth.router, prefix="/auth")
app.include_router(predict.router, prefix="")


@app.on_event("startup")
async def on_startup() -> None:
    """Loga a inicialização da API."""
    logger.info("API iniciada")
