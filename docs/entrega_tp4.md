# HealthAssist API — Entrega TP4

**Autor:** Gabriel Oliveira Freitas · **Disciplina:** Análise e Segurança de Agentes de IA · **Data:** 2026-11-26
**Repositório:** healthassist-api · **LLM do agente:** Ollama local (`qwen2.5:7b`)

## Checklist das evidências obrigatórias

| # | Evidência | Onde | Status |
|---|-----------|------|--------|
| 1 | Notebook de classificação (TF-IDF + modelo, GridSearchCV, matriz de confusão, métricas por classe, baseline) | `eda/classificacao_tp4.ipynb` · `eda/classificacao_tp4.py` · `eda/classificacao_relatorio.md` · `eda/matriz_confusao.png` | ✅ |
| 2 | API com `POST /classify` funcionando + modelo serializado + JWT | `app/routes/classify.py` · `app/classifier.py` · `models/intent_classifier.joblib` · `models/manifest.json` | ✅ |
| 3 | Agente (Agent + Runner + @function_tool) com conversa de 3 turnos | `scripts/agent_triagem.py` · `docs/agente_tp4.md` | ✅ |
| 4 | Log parcial de pentest (JWT, recon, BOLA/BFLA/IDOR, fuzzing) | `pentest/log_pentest_tp4.md` · `pentest/evidencias/` | ✅ |

Testes: `pytest tests/ -v` → **66 passed** (inclui `tests/test_classify.py`).

---

## Evidência 2 — Endpoint `POST /classify`

Rota protegida por JWT que recebe um texto, passa pelo modelo treinado (carregado com
checagem de integridade SHA-256 + versão do scikit-learn) e retorna a intenção prevista
com a probabilidade.

**Contrato:** request `{"text": "<1–4000 chars>"}` → response
`{"intent": "<classe>", "probability": <0..1>, "model_version": "healthassist-intents-tp4-v1"}`.
`extra="forbid"` rejeita campos não previstos (422); sem Bearer → 401; modelo indisponível → 503.

**Evidência de execução (curl, API em `127.0.0.1:8710`):**

```
# sem token
$ curl -s -o /dev/null -w "%{http_code}" -X POST .../classify -d '{"text":"dor no joelho"}'
401

# com token
$ curl -s -X POST .../classify -H "Authorization: Bearer <JWT>" \
       -d '{"text":"Qual o melhor tratamento para capsulite adesiva?"}'
{"intent":"Tratamento","probability":0.959,"model_version":"healthassist-intents-tp4-v1"}

$ ... -d '{"text":"Como encontrar um bom reumatologista na minha cidade?"}'
{"intent":"Escolha de profissionais de saúde","probability":0.450,...}

$ ... -d '{"text":"O que é artrite gotosa?"}'
{"intent":"Epidemiologia","probability":0.311,...}
```

O modelo serializado (`models/intent_classifier.joblib`, SHA-256
`2a53a925…67ec7`) é um `Pipeline` autossuficiente (TF-IDF nativo + LogisticRegression):
carrega apenas com `scikit-learn==1.9.1`, sem depender do script de treino.
