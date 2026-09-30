"""Middleware que adiciona headers de segurança HTTP a todas as respostas."""
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Swagger/Redoc precisam carregar scripts e estilos externos para renderizar;
# a API "de verdade" (JSON) não carrega nada, então recebe um CSP restritivo.
_DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")
_API_CSP = "default-src 'none'; frame-ancestors 'none'"
_DOCS_CSP = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://fastapi.tiangolo.com"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adiciona HSTS, X-Frame-Options, X-Content-Type-Options, CSP e Referrer-Policy."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Injeta os headers de segurança na resposta antes de devolvê-la ao cliente."""
        response = await call_next(request)

        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        is_docs = request.url.path.startswith(_DOCS_PATHS)
        response.headers["Content-Security-Policy"] = _DOCS_CSP if is_docs else _API_CSP

        return response
