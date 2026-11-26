# Validação da documentação OpenAPI — HealthAssist API

**Como foi validado:** a aplicação foi subida localmente com o venv do repo
(`.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8701`), e os
endpoints de documentação foram consultados via `curl`. A app foi **encerrada**
ao fim da coleta (porta 8701 liberada). A porta 8800 (alvo de outro worker) não
foi tocada.

## Disponibilidade dos endpoints de documentação

| Endpoint | Status HTTP | Resultado |
|---|---|---|
| `GET /openapi.json` | 200 | OpenAPI 3.1.0 — `HealthAssist API` v0.1.0 (6186 bytes, salvo em `openapi.json`) |
| `GET /docs` (Swagger UI) | 200 | Responde (Swagger self-hosted; CSP de docs permite cdn.jsdelivr.net) |
| `GET /health` | 200 | Sanity check |

## Schemas de entrada (request) e saída (response) por rota

| Método | Rota | Schema de entrada (requestBody) | Schemas de saída (responses) |
|---|---|---|---|
| GET | `/health` | n/a (GET sem corpo) | `200: HealthResponse` |
| POST | `/auth/token` | `TokenRequest` | `200: TokenResponse`, `401`, `422`, `429` (documentados) |
| POST | `/predict` | `PredictRequest` | `200: PredictResponse`, `422: HTTPValidationError` |
| GET | `/triagens/{triagem_id}` | n/a (parâmetro de path `triagem_id: integer`) | `200: TriagemResponse`, `422: HTTPValidationError` |

**Componentes/schemas Pydantic expostos:** `HealthResponse`, `TokenRequest`,
`TokenResponse`, `PredictRequest`, `PredictResponse`, `TriagemResponse`,
`HTTPValidationError`, `ValidationError`.

## Conclusão

- Todas as rotas que recebem corpo (`POST /auth/token`, `POST /predict`) têm
  **schema de entrada** (modelo Pydantic com `extra="forbid"` e limites de
  tamanho) refletido no OpenAPI.
- Todas as rotas têm **schema de saída** tipado (modelo Pydantic) no `200`, e
  as rotas protegidas/validadas documentam os códigos de erro (401/422/429).
- O Swagger (`/docs`) e o `openapi.json` respondem 200.

Validação OK: a documentação OpenAPI cobre entrada e saída de todos os
endpoints.
