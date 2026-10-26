#!/usr/bin/env bash
# DAST: sobe a API com banco descartável, autentica como "alice" e roda o ZAP API scan
# (com Authorization, para exercitar /predict e /triagens, não só o 401).
# Falha (exit != 0) se o ZAP reportar alerta FAIL/WARN de Medium ou High.
# Uso: SECRET_KEY=... bash scripts/run_dast.sh   (requer docker)
set -euo pipefail

PORT="${PORT:-8000}"
WORK="$(mktemp -d)"
trap 'kill "${API_PID:-0}" 2>/dev/null || true' EXIT

export DATABASE_URL="sqlite:///${WORK}/dast.db"
export SEED_ADMIN_PASSWORD="dast-admin-$RANDOM$RANDOM"
export SEED_ALICE_PASSWORD="dast-alice-$RANDOM$RANDOM"
export SEED_BOB_PASSWORD="dast-bob-$RANDOM$RANDOM"
export RATE_LIMIT_AUTH="1000/minute"   # o scan faz muitas chamadas; o limite real é testado no pytest

python -m scripts.seed
python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" >"$WORK/api.log" 2>&1 &
API_PID=$!
for _ in $(seq 1 30); do curl -sf "http://localhost:$PORT/health" >/dev/null && break; sleep 1; done

TOKEN="$(curl -sf -X POST "http://localhost:$PORT/auth/token" -H 'Content-Type: application/json' \
  -d "{\"username\":\"alice\",\"password\":\"$SEED_ALICE_PASSWORD\"}" | python -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')"

mkdir -p zap-out && chmod 777 zap-out
# Sem -I: qualquer WARN/FAIL dos alertas não-informativos derruba o gate.
docker run --rm --network host -v "$(pwd)/zap-out:/zap/wrk:rw" \
  -e ZAP_AUTH_HEADER=Authorization -e ZAP_AUTH_HEADER_VALUE="Bearer $TOKEN" \
  ghcr.io/zaproxy/zaproxy:stable zap-api-scan.py \
  -t "http://localhost:$PORT/openapi.json" -f openapi -r zap-report.html -J zap-report.json
