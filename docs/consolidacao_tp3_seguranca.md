# Consolidação das evidências de segurança — TP3 (HealthAssist API)

Checklist de resposta ao feedback do professor sobre o TP3. Cada item aponta a
evidência concreta no repositório. Coletado em 2026-11-26 com o venv do projeto
(`.venv/bin/python`, Python 3.12.3, pytest 9.1.1).

## Resumo do feedback → status

| # | Pedido do professor | Status | Evidência |
|---|---|---|---|
| a | Suíte pytest com ≥5 casos verificáveis incluindo RATE LIMITING, com resultados de execução | ✅ OK | 62 testes, todos passam; ver abaixo e `docs/evidencias/pytest_resultado.txt` |
| b | Comprovar que os testes passam no CI (GitHub Actions) com gate | ✅ OK | Workflow `security-tests` verde em `main`; `docs/evidencias/ci_runs.txt` |
| c | Checklist final OWASP ZAP com Medium/High resolvidos | ✅ OK | `docs/auditoria_final_tp3.md` (seção "Checklist final OWASP ZAP") |
| d | Validar documentação OpenAPI (schemas de entrada e saída) | ✅ OK | `docs/evidencias/openapi.json` + `docs/evidencias/openapi_validacao.md` |

## (a) Suíte pytest — ≥5 casos verificáveis

Os 5 eixos exigidos estão cobertos (todos em `tests/`), com folga:

| Eixo exigido | Teste(s) | O que verifica |
|---|---|---|
| Autenticação (401 sem token / token inválido) | `test_security.py::test_predict_sem_token_retorna_401`, `test_token_com_assinatura_invalida_e_rejeitado`, `test_token_expirado_e_rejeitado`, `test_token_alg_none_e_rejeitado` | `/predict` sem token, assinatura forjada, token expirado e `alg=none` → todos 401 |
| Autorização / BOLA (um usuário não lê recurso de outro) | `test_security.py::test_bola_nao_acessa_triagem_de_outro_usuario`, `test_web_attacks.py::test_bola_por_enumeracao_de_ids_nunca_retorna_dados_alheios` | Bob recebe o mesmo 404 para triagem da Alice e para id inexistente; varredura de ids não vaza nada |
| Validação de entrada (422 em malformado/campo extra) | `test_security.py::test_campo_extra_no_body_e_rejeitado`, `test_predict_valida_formato_e_tamanho` (7 casos), `test_login_rejeita_campo_extra` | `extra="forbid"`, listas vazias/grandes, tipos errados → 422 |
| **Rate limiting (excede limite → 429)** | `test_security.py::test_rate_limit_em_auth_token`, `test_web_attacks.py::test_rate_limit_nao_e_burlado_trocando_username` | Após 5 req em `/auth/token` a 6ª retorna 429; trocar username não zera o contador (limite por IP) |
| Cabeçalhos / headers de segurança | `test_security.py::test_headers_de_seguranca_presentes`, `test_web_attacks.py::test_headers_de_seguranca_em_respostas_de_erro`, `test_nao_expoe_header_server_com_versao_de_framework` | HSTS, X-Frame-Options DENY, nosniff, CSP e CORP presentes (inclusive em 401/404/422) |

Determinismo: `tests/conftest.py` recria o banco em memória e chama
`limiter.reset()` antes de cada teste (fixture autouse `_fresh_database`), o que
torna o teste de rate limit estável.

## (a) Resultado da execução

```
62 passed, 1 warning in 2.63s
```

Saída completa em `docs/evidencias/pytest_resultado.txt`. Com cobertura (igual
ao gate do CI): `Required test coverage of 90% reached. Total coverage: 98.37%`.

- Testes adicionados nesta rodada: **nenhum** — o eixo de rate limiting já
  existia e foi confirmado. Nenhum teste precisou ser corrigido (0 falhas).

## (b) Gate de CI (GitHub Actions) — OK

`.github/workflows/security-tests.yml`:
- Job `tests` roda `pytest tests/ -v --cov=app --cov=scripts --cov-report=term-missing --cov-fail-under=90` → falha o build se qualquer teste falhar ou a cobertura cair abaixo de 90%.
- Job `gates` (`needs: [lint, sast, sca, tests, dast]`, `if: always()`) faz `exit 1` se qualquer gate tiver resultado `failure`/`cancelled`/`skipped`. É o único check a exigir em branch protection.
- Última execução em `main` (run `45228474767`, 2026-11-23): todos os jobs ✅, incluindo "Gate: testes + cobertura >= 90%". Evidência em `docs/evidencias/ci_runs.txt`.
- `gh` autenticado como `GabrielOliveiraFreitas`; histórico de runs do workflow salvo.

Observação: o bloqueio de merge em si depende de *branch protection* no GitHub
(Settings → Branches → Require status checks → `gates`), que não é configurável
por arquivo no repositório (ação manual, já anotada no item 16 da auditoria).

## (c) Checklist OWASP ZAP — Medium/High resolvidos — OK

Resumo oficial do re-scan (`docs/zap-report.html`, "Summary of Alerts"):
**High: 0 · Medium: 0 · Low: 0 · Informational: 4**.

- Findings **High/Medium**: 0 detectados em qualquer execução → nada pendente.
- Único finding acionável histórico: **Low** — Cross-Origin-Resource-Policy
  Header Missing [90004] → corrigido em `app/middleware/security_headers.py:29`;
  re-scan `WARN-NEW: 0`.
- 4 itens Informational aceitos com justificativa.

Checklist por finding e tabela-resumo em
`docs/auditoria_final_tp3.md` (seção "Checklist final OWASP ZAP (por finding)").

## (d) OpenAPI validada — OK

`openapi.json` (OpenAPI 3.1.0) baixado da app local; `/docs` responde 200.
Todas as rotas com corpo têm schema de entrada Pydantic e todas têm schema de
saída tipado (detalhamento em `docs/evidencias/openapi_validacao.md`).

## Arquivos de evidência (desta consolidação)

- `docs/evidencias/pytest_resultado.txt` — saída completa do pytest (62 passed).
- `docs/evidencias/openapi.json` — especificação OpenAPI coletada da app.
- `docs/evidencias/openapi_validacao.md` — resumo da validação OpenAPI.
- `docs/evidencias/ci_runs.txt` — histórico/execução do workflow `security-tests`.
- `docs/auditoria_final_tp3.md` — checklist final OWASP ZAP (atualizado).
