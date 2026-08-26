# HealthAssist API — Triagem Médica

API de triagem médica com autenticação JWT, construída em FastAPI. Este repositório
corresponde à Fase 2 (estrutura base da API) do Projeto de Bloco: **LGPD de Saúde +
Proteção contra DoS**.

## Objetivo do Projeto

Servir como backend de um sistema de atendimento/triagem médica que, ao longo do
bloco, vai incorporar um modelo de EDA/ML para classificar sintomas e um agente de
IA para interação com o usuário. Nesta fase, o foco é ter uma API FastAPI segura,
modular e autenticada via JWT, com a rota `/predict` retornando um placeholder até
a integração com o modelo real.

## Estrutura de Pastas

```
healthassist-api/
├── app/
│   ├── main.py                 # Entry point, app FastAPI
│   ├── config.py               # Variáveis de ambiente (SECRET_KEY, ALGORITHM, etc.)
│   ├── models/
│   │   └── schemas.py          # Pydantic models (request/response)
│   ├── routes/
│   │   ├── health.py           # GET /health
│   │   ├── auth.py             # POST /auth/token
│   │   └── predict.py          # POST /predict (protegida por JWT)
│   └── security/
│       └── jwt_handler.py      # Geração/validação de JWT
├── requirements.txt
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

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Copie o arquivo de variáveis de ambiente
cp .env.example .env
```

## Execução

```bash
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`. Documentação interativa (Swagger) em
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

# Predict com token válido — deve retornar 200
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer <seu_token_aqui>" \
  -H "Content-Type: application/json" \
  -d '{"symptoms":["febre","tosse"]}'
```

## Segurança & Autenticação

- Autenticação via JWT (HS256), emitido em `/auth/token` e validado via
  `OAuth2PasswordBearer` (`tokenUrl="auth/token"`).
- Token expira em 1 hora (configurável via `TOKEN_EXPIRATION_HOURS` no `.env`).
- Usuário de exemplo (MVP, hardcoded): `admin` / `senha123`. Isso é temporário e
  será substituído por uma base de usuários real em fase futura.
- `SECRET_KEY` deve ser definida no `.env` — nunca commitar o `.env` real
  (já está no `.gitignore`).

Veja [`docs/DFD.md`](docs/DFD.md) para o diagrama de fluxo de dados, trust
boundaries e análise CIA (Confidencialidade, Integridade, Disponibilidade).

## Status do Projeto

- ✅ Fase 2: API FastAPI + JWT (este repositório)
- ⏳ Fase 1: EDA do dataset de sintomas/atendimento (em andamento, por outro
  membro da equipe)
- ⏳ Fase 3: LGPD (documentação DFD) + proteção contra DoS (rate limiting,
  circuit breaker)
- ⏳ Fase 4: Integração do modelo de EDA/ML na rota `/predict`

## Dataset

A escolha, documentação de fonte/licença e a EDA do dataset de atendimento estão
sendo conduzidas por outro integrante da equipe e serão adicionadas em
`data/` e `notebooks/` neste mesmo repositório.
