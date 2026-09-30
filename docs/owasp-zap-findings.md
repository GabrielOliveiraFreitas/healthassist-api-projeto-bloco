# Relatório de Auditoria OWASP ZAP — HealthAssist API

## Metodologia

- **Ferramenta:** OWASP ZAP (imagem oficial `zaproxy/zap-stable`, via Docker).
- **Modo:** `zap-api-scan.py` — scan orientado por especificação OpenAPI (`-f
  openapi`), a forma recomendada pelo próprio ZAP para APIs REST em vez do
  baseline "spider" tradicional (que depende de links HTML, inexistentes aqui).
- **Alvo:** `http://localhost:8000/openapi.json`, com a API rodando
  localmente (`uvicorn app.main:app`) e o container ZAP na rede do host
  (`--network host`).
- **Escopo:** rotas expostas pelo `openapi.json` — `GET /health`,
  `POST /auth/token`, `POST /predict`, `GET /triagens/{id}`. O scan foi
  executado **sem credenciais** (sem JWT), então as rotas protegidas
  respondem 401 às tentativas do ZAP — o que é o comportamento esperado e
  correto. A cobertura de autorização/BOLA em si (usuário só acessa o
  próprio recurso) é responsabilidade da suíte `tests/test_security.py`, não
  do ZAP: o ZAP audita a superfície HTTP/transporte (headers, injeção,
  vazamento de informação), os testes de unidade/integração auditam a lógica
  de negócio autenticada.
- **Comando:**
  ```bash
  docker run --rm --network host -v "$(pwd)/zap-work:/zap/wrk:rw" zaproxy/zap-stable \
    zap-api-scan.py -t http://localhost:8000/openapi.json -f openapi \
    -r zap-report.html -J zap-report.json -w zap-report.md -I
  ```
- **Relatório completo:** [`docs/zap-report.html`](zap-report.html).

## Resultado

Primeira execução — **1 finding acionável**, sem nenhum de severidade Medium
ou High:

| Severidade | Finding | Rotas afetadas |
|---|---|---|
| Low | Cross-Origin-Resource-Policy Header Missing or Invalid [90004] | `GET /health`, `GET /openapi.json` |

O restante (117 regras passivas/ativas) passou sem alertas: sem SQL
Injection, XSS, CSRF, vazamento de código-fonte, Server-Side Template
Injection, XXE, path traversal, etc.

### Finding: Cross-Origin-Resource-Policy Header Missing or Invalid

- **O que foi detectado:** as respostas de `/health` e `/openapi.json` não
  enviavam o header `Cross-Origin-Resource-Policy`.
- **Por que é um problema:** sem esse header, outra origem pode embutir a
  resposta (por exemplo via `<img>`/`fetch` com `no-cors`) em ataques do
  tipo Spectre/side-channel para inferir conteúdo entre origens. Risco baixo
  aqui porque as respostas não são sensíveis, mas é uma correção de custo
  zero.
- **Como foi corrigido:** adicionado `Cross-Origin-Resource-Policy:
  same-origin` em todas as respostas, junto dos demais headers de segurança,
  em `app/middleware/security_headers.py`.
- **Status:** ✅ Corrigido. Re-scan confirmou `WARN-NEW: 0` após a correção
  (ver segunda execução abaixo).

## Re-scan (após a correção)

```
FAIL-NEW: 0	FAIL-INPROG: 0	WARN-NEW: 0	WARN-INPROG: 0	INFO: 0	IGNORE: 0	PASS: 118
```

Nenhum finding de severidade Low, Medium ou High restante. Os 4 alertas que
seguem aparecendo são puramente **Informational** (classificação do próprio
ZAP, não vulnerabilidades) e foram avaliados como risco aceito:

| Finding (Informational) | Rotas | Avaliação |
|---|---|---|
| A Client Error response code was returned by the server | paths inexistentes / auth ausente | Esperado: 401/404 são as respostas corretas para requisições não autenticadas ou rotas inexistentes que o próprio ZAP tenta descobrir (fuzzing de path). |
| Authentication Request Identified | `POST /auth/token` | Apenas identifica que a rota é de login — não é uma falha. |
| Non-Storable Content | `/predict`, `/auth/token`, `/triagens/{id}` | Correto e desejado: dado de saúde/token não deve ser cacheável. |
| Storable and Cacheable Content | `/health`, `/openapi.json` | Aceitável: nenhuma das duas expõe dado sensível ou específico de usuário. |

**Risco aceito:** os 4 itens acima não exigem ação — refletem comportamento
correto da API, não fragilidades.

## Limitações do scan

- Como o ZAP não recebeu um JWT válido, ele não exercitou os caminhos
  autenticados de `/predict` e `/triagens/{id}` além do handshake 401. A
  cobertura de BOLA, ownership e validação de payload autenticado vem dos
  testes pytest (`tests/test_security.py`), que rodam com tokens reais.
- O scan foi feito contra a API local (HTTP, sem TLS); o header HSTS está
  configurado no middleware e será efetivo quando a API for servida atrás de
  HTTPS em produção.
