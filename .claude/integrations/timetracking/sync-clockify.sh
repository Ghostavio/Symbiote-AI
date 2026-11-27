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
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
if ! INTERVAL=$(python3 "$PROJECT_ROOT/scripts/time-entry-interval.py" "$START_TIME" "$END_TIME"); then
  exit 1
fi
START_UTC=$(INTERVAL_JSON="$INTERVAL" python3 -c 'import json, os; print(json.loads(os.environ["INTERVAL_JSON"])["start_utc"])')
END_UTC=$(INTERVAL_JSON="$INTERVAL" python3 -c 'import json, os; print(json.loads(os.environ["INTERVAL_JSON"])["end_utc"])')

if [[ -z "${CLOCKIFY_API_TOKEN:-}" ]]; then
  echo "[Clockify] SKIP — CLOCKIFY_API_TOKEN não configurado"
  exit 0
fi
if [[ -z "${CLOCKIFY_WORKSPACE_ID:-}" ]]; then
  echo "[Clockify] SKIP — CLOCKIFY_WORKSPACE_ID não configurado"
  exit 0
fi

PROJECT_ID="${CLOCKIFY_PROJECT_ID:-}"

BODY=$(CLOCKIFY_START="$START_UTC" CLOCKIFY_END="$END_UTC" \
  DESCRIPTION="$DESCRIPTION" PROJECT_ID="$PROJECT_ID" \
  python3 -c '
import json, os
body = {
    "start": os.environ["CLOCKIFY_START"],
    "end": os.environ["CLOCKIFY_END"],
    "description": os.environ["DESCRIPTION"],
    "billable": True,
}
if os.environ["PROJECT_ID"]:
    body["projectId"] = os.environ["PROJECT_ID"]
print(json.dumps(body))
')

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
  exit 1
fi
