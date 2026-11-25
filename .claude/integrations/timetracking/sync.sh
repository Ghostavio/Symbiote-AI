#!/usr/bin/env bash
# ============================================================
# sync.sh — Wrapper opcional para quem também registra horas no Clockify.
#
# Registra uma entrada de tempo em AMBAS as plataformas:
# - 7pace Timetracker (via scripts/sync-7pace.sh)
# - Clockify (via sync-clockify.sh local)
#
# Uso idêntico ao sync-7pace.sh do repo.
# ============================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

SYNC_7PACE="$PROJECT_ROOT/scripts/sync-7pace.sh"
SYNC_CLOCKIFY="$SCRIPT_DIR/sync-clockify.sh"

# Parse para separar: argumentos pro 7pace e descrição (para construir prefixo Clockify)
DESCRIPTION=""
WORK_ITEM_ID=""
START_TIME=""
END_TIME=""
DRY_RUN_FLAG=""

# Copiar todos os args originais
ORIG_ARGS=("$@")

# Extrair valores específicos para o Clockify sem perder os originais
while [[ $# -gt 0 ]]; do
  case "$1" in
    --description) DESCRIPTION="$2"; shift 2 ;;
    --work-item-id) WORK_ITEM_ID="$2"; shift 2 ;;
    --start) START_TIME="$2"; shift 2 ;;
    --end) END_TIME="$2"; shift 2 ;;
    --dry-run) DRY_RUN_FLAG="--dry-run"; shift ;;
    *) shift ;;
  esac
done

# 1. Sincronizar com 7pace (passa argumentos originais)
"$SYNC_7PACE" "${ORIG_ARGS[@]}"

# 2. Sincronizar com Clockify (com prefixo {ID}: exceto Daily)
if [[ "$DESCRIPTION" == "Daily" ]]; then
  CLOCKIFY_DESC="Daily"
else
  CLOCKIFY_DESC="${WORK_ITEM_ID}: ${DESCRIPTION}"
fi

"$SYNC_CLOCKIFY" \
  --description "$CLOCKIFY_DESC" \
  --start "$START_TIME" \
  --end "$END_TIME" \
  $DRY_RUN_FLAG
