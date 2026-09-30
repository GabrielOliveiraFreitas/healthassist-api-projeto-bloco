# HealthAssist API — Triagem Médica

API de triagem médica com autenticação JWT, construída em FastAPI. Este repositório
corresponde ao TP2 do Projeto de Bloco: **LGPD de Saúde + Proteção contra DoS** —
hardening OWASP Top 10 sobre a base entregue no TP1.

## Objetivo do Projeto

Servir como backend de um sistema de atendimento/triagem médica que, ao longo do
bloco, vai incorporar um modelo de EDA/ML para classificar sintomas e um agente de
IA para interação com o usuário. Nesta fase, a API ganhou persistência real
(SQLModel), verificação de ownership (BOLA), headers de segurança, CORS com
allowlist e rate limiting — além de ter sido auditada com OWASP ZAP.

## Estrutura de Pastas

```
healthassist-api/
├── app/
│   ├── main.py                 # Entry point: FastAPI app, middlewares, rate limiter
│   ├── config.py               # Variáveis de ambiente (SECRET_KEY, CORS_ORIGINS, etc.)
│   ├── db.py                   # Engine SQLModel + dependency de sessão por requisição
│   ├── rate_limit.py           # Limiter (slowapi) compartilhado
│   ├── models/
│   │   ├── schemas.py          # Pydantic models (request/response, extra="forbid")
│   │   └── entities.py         # Entidades SQLModel (tabelas) — ex.: Triagem
│   ├── routes/
│   │   ├── health.py           # GET /health
│   │   ├── auth.py             # POST /auth/token (rate limited)
│   │   ├── predict.py          # POST /predict (protegida por JWT, persiste Triagem)
│   │   └── triagens.py         # GET /triagens/{id} (protegida por JWT + BOLA)
│   ├── middleware/
│   │   └── security_headers.py # HSTS, X-Frame-Options, X-Content-Type-Options, CSP
│   └── security/
│       └── jwt_handler.py      # Geração/validação de JWT
├── tests/                      # Suite pytest (segurança: BOLA, sem token, extra field)
├── docs/
│   ├── DFD.md                  # Data flow diagram + trust boundaries + CIA
│   └── owasp-zap-findings.md   # Findings do scan OWASP ZAP e como foram tratados
├── requirements.txt
├── requirements-dev.txt        # Dependências extras para rodar os testes
├── .env.example
└── README.md
```

## Instalação

Pré-requisitos: Python 3.10+ (projeto testado com 3.12).

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd healthassist-api

# 2. Crie e ative um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate      # Linux/Mac
# .venv\Scripts\activate       # Windows

# 3. Instale as dependências (adicione -r requirements-dev.txt para rodar os testes)
pip install -r requirements.txt

# 4. Copie o arquivo de variáveis de ambiente
cp .env.example .env
```

## Execução

```bash
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000` e cria o banco SQLite (`healthassist.db`)
automaticamente no startup. Documentação interativa (Swagger) em
`http://localhost:8000/docs`.

## Testando as rotas

```bash
# Health check (sem autenticação) — deve retornar 200
curl -X GET http://localhost:8000/health

# Obter token JWT
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha123"}'

# Predict sem token — deve retornar 401
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"symptoms":["febre","tosse"]}'

# Predict com token válido — persiste a triagem e devolve o id
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer <seu_token_aqui>" \
  -H "Content-Type: application/json" \
  -d '{"symptoms":["febre","tosse"]}'

# Consultar a triagem pelo id — só funciona para o dono (BOLA), senão 404
curl http://localhost:8000/triagens/1 \
  -H "Authorization: Bearer <seu_token_aqui>"
```

### Rodando os testes

```bash
pip install -r requirements-dev.txt
pytest tests/
```

## Segurança & Autenticação

- Autenticação via JWT (HS256), emitido em `/auth/token` e validado via
  `OAuth2PasswordBearer` (`tokenUrl="auth/token"`).
- Token expira em 1 hora (configurável via `TOKEN_EXPIRATION_HOURS` no `.env`).
- Usuário de exemplo (MVP, hardcoded): `admin` / `senha123`. Isso é temporário e
  será substituído por uma base de usuários real em fase futura.
- `SECRET_KEY` deve ser definida no `.env` — nunca commitar o `.env` real
  (já está no `.gitignore`).
- **Pydantic `extra="forbid"`** em todos os schemas de entrada (`TokenRequest`,
  `PredictRequest`): qualquer campo fora do schema é rejeitado com 422, em vez
  de ser silenciosamente ignorado.
- **Persistência com SQLModel**: `/predict` grava um registro `Triagem`
  (sintomas + resultado) vinculado ao usuário autenticado. Todo acesso ao banco
  usa queries parametrizadas via ORM (`session.exec(select(...))`), nunca SQL cru.
- **BOLA (Broken Object Level Authorization)**: `GET /triagens/{id}` filtra por
  `id` **e** pelo dono na mesma query. Se o registro não existir ou pertencer a
  outro usuário, a resposta é sempre `404` — evita usar o ID como oráculo para
  descobrir se um recurso de outra pessoa existe.
- **Headers de segurança** (`app/middleware/security_headers.py`): HSTS,
  `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: no-referrer` e Content-Security-Policy — restritivo
  (`default-src 'none'`) nas rotas da API e um pouco mais permissivo só em
  `/docs`/`/redoc`/`/openapi.json`, que precisam carregar os assets do Swagger.
- **CORS com allowlist explícita** (`CORS_ORIGINS` no `.env`, nunca `*`).
- **Rate limiting em `/auth/token`** (`RATE_LIMIT_AUTH`, padrão `5/minute` por
  IP, via `slowapi`) para dificultar brute force de senha: poucas tentativas
  legítimas de login por minuto vs. resistência a ataques automatizados.

Veja [`docs/DFD.md`](docs/DFD.md) para o diagrama de fluxo de dados, trust
boundaries e análise CIA, e [`docs/owasp-zap-findings.md`](docs/owasp-zap-findings.md)
para os achados do scan OWASP ZAP e como cada um foi tratado.

## Status do Projeto

- ✅ TP1 (Fase 2): API FastAPI + JWT
- ✅ TP2: SQLModel, BOLA, headers de segurança, CORS, rate limiting, scan ZAP e
  testes pytest de segurança (este repositório)
- ⏳ EDA do dataset de sintomas/atendimento (por outro membro da equipe)
- ⏳ Integração do modelo de EDA/ML na rota `/predict`

## Dataset

A escolha, documentação de fonte/licença e a EDA do dataset de atendimento estão
sendo conduzidas por outro integrante da equipe e serão adicionadas em
`data/` e `notebooks/` neste mesmo repositório.
