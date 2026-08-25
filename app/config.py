"""Configuração da aplicação carregada a partir de variáveis de ambiente."""
import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-insecure")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
TOKEN_EXPIRATION_HOURS: int = int(os.getenv("TOKEN_EXPIRATION_HOURS", "1"))
DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
