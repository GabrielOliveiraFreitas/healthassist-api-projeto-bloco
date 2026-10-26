# Auditoria final de segurança — HealthAssist API (TP3)

Escopo: API FastAPI em `app/`, preparada como alvo de pentest do TP4/TP5.
Evidências de autorização/BOLA vêm dos testes autenticados (`pytest tests/ -v`, 62 casos, 98% de cobertura); evidências de superfície HTTP vêm do scan ZAP
([`owasp-zap-findings.md`](owasp-zap-findings.md)). As duas fontes são distintas.

## Checklist

| # | Item | Status | Evidência |
|---|---|---|---|
| 1 | Findings ZAP Medium/High pendentes | ✅ Resolvido (nenhum existiu) | Único finding acionável (Low, CORP header) corrigido; re-scan com `WARN-NEW: 0`. |
| 2 | Autenticação JWT (HS256, exp 1h, OAuth2 Bearer) | ✅ Resolvido | Testes: sem token, expirado, assinatura forjada, `alg=none` → 401. |
| 3 | Credenciais fixas no código (apontado no TP1) | ✅ Resolvido | Usuários na tabela `User`; sem usuário/senha no código. Seed via `scripts/seed.py` com senhas do ambiente. |
| 4 | Senha em texto puro (apontado no TP1) | ✅ Resolvido | Hash scrypt com salt (`app/security/passwords.py`); comparação em tempo constante; verificação fictícia para usuário inexistente (sem enumeração por resposta/timing). |
| 5 | `SECRET_KEY` com fallback inseguro (apontado no TP1) | ✅ Resolvido | `app/config.py` levanta erro se ausente ou < 32 caracteres. |
| 6 | Camada de banco (apontado no TP1) | ✅ Resolvido | SQLModel: tabelas `User` e `Triagem`; queries via ORM, sem SQL cru. |
| 7 | BOLA | ✅ Resolvido | `GET /triagens/{id}` filtra por `id` e `owner`; 404 idêntico para inexistente e alheio (teste). |
| 8 | Validação de entrada | ✅ Resolvido | `extra="forbid"` + limites (1–20 sintomas, ≤100 chars, user ≤64, senha ≤128); 7 casos parametrizados + SQLi tratado como dado. |
| 9 | Rate limiting em `/auth/token` | ✅ Resolvido, com ressalva | 5/min por IP (slowapi); teste confirma 429. Ressalva: contador em memória e por IP — não vale para múltiplas instâncias nem atrás de proxy sem tratar `X-Forwarded-For`. |
| 10 | Headers (HSTS, XFO, nosniff, CSP, CORP) e CORS allowlist | ✅ Resolvido | Testes de headers e de CORS. |
| 11 | HSTS efetivo | ⚠️ Aceito | Só tem efeito sob HTTPS; o ambiente de teste é HTTP local. |
| 12 | Rate limit só em `/auth/token` | ⚠️ Aceito | `/predict` exige JWT; limite global fica para o T2 se o pentest mostrar abuso. |
| 13 | Tokens sem revogação / sem refresh | ⚠️ Aceito | Expiração curta (1h) limita a janela; sem lista de revogação no MVP. |
| 14 | `/docs` bem documentado | ✅ Resolvido | Descrição, tags, respostas 401/404/422/429 e exemplos nos schemas. |
| 15 | CI/CD com gates | ✅ Resolvido | `.github/workflows/security-tests.yml`: lint (ruff), SAST (bandit), SCA (pip-audit), testes com cobertura ≥ 90% e DAST (ZAP autenticado). Teste negativo local: cada ferramenta retorna exit 1 com código/dep/teste ruim. |
| 15b | Dependências com CVE | ✅ Resolvido | `pip-audit` achou CVEs em starlette 0.27, anyio 3.7, fastapi 0.104, pyjwt 2.8, python-multipart 0.0.6; atualizadas (fastapi 0.162, starlette 1.10 etc.). Hoje: "No known vulnerabilities found". |
| 15c | XSS | ✅ Resolvido | API só serve JSON (`nosniff`, CSP `default-src 'none'`); testes de XSS armazenado e refletido; ZAP: regras de XSS em PASS. |
| 16 | Bloquear merge se o CI falhar | ⚠️ Ação manual | Exige *branch protection* no GitHub (Settings → Branches → Require status checks → `gates`); não é configurável por arquivo no repositório. |

## Pronto como alvo de pentest

Verificado localmente em 26/10/2026 (uvicorn real + SQLite + seed):

- `GET /health` → 200; `GET /docs` → 200; `POST /predict` sem token → 401.
- Login de `alice` → JWT; `POST /predict` → 200 com `id`; `GET /triagens/{id}` de outro usuário → 404; do próprio → 200.
- Sem erros no log do servidor.

Para reproduzir o ambiente de alvo:

```bash
cp .env.example .env     # preencha SECRET_KEY e SEED_*_PASSWORD
python -m scripts.seed   # usuários admin/alice/bob + 1 triagem de alice e 1 de bob
uvicorn app.main:app
```

Dados de teste: `alice` e `bob` (usuários comuns, para testar BOLA entre eles)
e `admin`. Triagem 1 pertence a `alice`, 2 a `bob`.

## DAST autenticado (ZAP, 26/10/2026)

`bash scripts/run_dast.sh` sobe a API com seed, loga como `alice` e roda o
`zap-api-scan.py` **com o header Authorization**, então `/predict` e
`/triagens/{id}` foram exercitados com sessão válida (o scan do TP2 não tinha JWT).
Resultado: `FAIL-NEW: 0  WARN-NEW: 0  PASS: 120`. O rate limit foi elevado só
nesse scan (ele faz centenas de chamadas); o limite real é coberto pelo pytest.
O mesmo script roda no CI (job `dast`).

## Riscos residuais conhecidos (para o pentest)

- Rate limit por IP em memória (item 9).
- Sem revogação de token (item 13).
- Sem HTTPS no ambiente local (item 11).
- BOLA/autorização continua dependendo de testes próprios: o ZAP não sabe quais
  recursos pertencem a quem. O Burp Suite não foi usado (ferramenta interativa);
  ver README para a configuração de teste manual.
