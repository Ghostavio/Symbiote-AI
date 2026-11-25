#!/usr/bin/env bash
# ============================================================
# sync-clockify.sh — Registra uma entrada de tempo no Clockify.
#
# Chamado pelo wrapper sync.sh desta pasta. Também pode ser
# usado diretamente.
#
# Requer: .env no mesmo diretório com CLOCKIFY_API_TOKEN,
#         CLOCKIFY_WORKSPACE_ID e CLOCKIFY_PROJECT_ID.
# ============================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Carregar credenciais
if [[ -f "$SCRIPT_DIR/.env" ]]; then
  set -a
  source "$SCRIPT_DIR/.env"
  set +a
fi

# --- Parse argumentos ---
DESCRIPTION=""
START_TIME=""
END_TIME=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --description) DESCRIPTION="$2"; shift 2 ;;
    --start) START_TIME="$2"; shift 2 ;;
    --end) END_TIME="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "[Clockify] Argumento desconhecido: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$DESCRIPTION" || -z "$START_TIME" || -z "$END_TIME" ]]; then
  echo "[Clockify] ERRO: --description, --start e --end são obrigatórios." >&2
  exit 1
fi

if [[ -z "${CLOCKIFY_API_TOKEN:-}" ]]; then
  echo "[Clockify] SKIP — CLOCKIFY_API_TOKEN não configurado"
  exit 0
fi
if [[ -z "${CLOCKIFY_WORKSPACE_ID:-}" ]]; then
  echo "[Clockify] SKIP — CLOCKIFY_WORKSPACE_ID não configurado"
  exit 0
fi

PROJECT_ID="${CLOCKIFY_PROJECT_ID:-}"

# Converter timestamps de Z (UTC) para -03:00 (BRT)
# Os timestamps do workflow representam horário local, mas usam sufixo Z por convenção.
# O 7pace corrige via timeZone:-180, mas o Clockify interpreta Z literalmente como UTC.
CLOCKIFY_START=$(echo "$START_TIME" | sed 's/Z$/-03:00/')
CLOCKIFY_END=$(echo "$END_TIME" | sed 's/Z$/-03:00/')

BODY=$(python3 -c "
import json
body = {
    'start': '$CLOCKIFY_START',
    'end': '$CLOCKIFY_END',
    'description': '$DESCRIPTION',
    'billable': True,
}
if '$PROJECT_ID':
    body['projectId'] = '$PROJECT_ID'
print(json.dumps(body))
")

if $DRY_RUN; then
  echo "[Clockify] DRY RUN — POST /time-entries"
  echo "$BODY" | python3 -m json.tool
  exit 0
fi

RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "X-Api-Key: $CLOCKIFY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$BODY" \
  "https://api.clockify.me/api/v1/workspaces/$CLOCKIFY_WORKSPACE_ID/time-entries")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" == "201" ]]; then
  ENTRY_ID=$(echo "$RESPONSE_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
  echo "[Clockify] OK — entry criada (ID: $ENTRY_ID)"
else
  echo "[Clockify] ERRO $HTTP_CODE — $RESPONSE_BODY" >&2
fi
