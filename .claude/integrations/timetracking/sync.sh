#!/usr/bin/env bash
# ============================================================
# sync.sh — Wrapper opcional para quem também registra horas no Clockify.
#
# Registra uma entrada de tempo em AMBAS as plataformas:
# - 7pace Timetracker (via scripts/sync-7pace.sh)
# - Clockify (via sync-clockify.sh local)
#
# Aceita os argumentos do sync-7pace.sh e --provider 7pace|clockify.
# ============================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

SYNC_7PACE="$PROJECT_ROOT/scripts/sync-7pace.sh"
SYNC_CLOCKIFY="$SCRIPT_DIR/sync-clockify.sh"

DESCRIPTION=""
WORK_ITEM_ID=""
START_TIME=""
END_TIME=""
PROVIDER="both"
SEVENPACE_ARGS=()
CLOCKIFY_FLAGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --description|--work-item-id|--start|--end|--activity-type|--provider)
      if [[ $# -lt 2 || "$2" == --* ]]; then
        echo "ERRO: informe um valor para $1." >&2
        exit 1
      fi
      ;;
  esac
  case "$1" in
    --description) DESCRIPTION="$2" ;;
    --work-item-id) WORK_ITEM_ID="$2" ;;
    --start) START_TIME="$2" ;;
    --end) END_TIME="$2" ;;
    --activity-type) ;;
    --provider)
      case "$2" in
        7pace|clockify) PROVIDER="$2" ;;
        *) echo "ERRO: --provider aceita 7pace ou clockify." >&2; exit 1 ;;
      esac
      shift 2
      continue
      ;;
    --dry-run)
      SEVENPACE_ARGS+=("$1")
      CLOCKIFY_FLAGS=("--dry-run")
      shift
      continue
      ;;
    *) echo "Argumento desconhecido: $1" >&2; exit 1 ;;
  esac
  SEVENPACE_ARGS+=("$1" "$2")
  shift 2
done

if [[ -z "$DESCRIPTION" || -z "$START_TIME" || -z "$END_TIME" || ! "$WORK_ITEM_ID" =~ ^[0-9]+$ ]]; then
  echo "ERRO: --description, --start, --end e --work-item-id numérico são obrigatórios." >&2
  exit 1
fi

if [[ "$PROVIDER" != "clockify" ]]; then
  "$SYNC_7PACE" "${SEVENPACE_ARGS[@]}"
fi
if [[ "$PROVIDER" == "7pace" ]]; then
  exit 0
fi
if [[ "$PROVIDER" == "clockify" ]]; then
  CLOCKIFY_FLAGS+=("--require-config")
fi

# Prefixo {ID}: no Clockify, exceto Daily
if [[ "$DESCRIPTION" == "Daily" ]]; then
  CLOCKIFY_DESC="Daily"
else
  CLOCKIFY_DESC="${WORK_ITEM_ID}: ${DESCRIPTION}"
fi

"$SYNC_CLOCKIFY" \
  --description "$CLOCKIFY_DESC" \
  --start "$START_TIME" \
  --end "$END_TIME" \
  ${CLOCKIFY_FLAGS[@]+"${CLOCKIFY_FLAGS[@]}"}
