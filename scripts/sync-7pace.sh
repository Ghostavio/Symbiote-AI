#!/usr/bin/env bash
# ============================================================
# sync-7pace.sh — Registra uma entrada de tempo no 7pace
# Timetracker via REST API v3.2.
#
# Uso:
#   ./scripts/sync-7pace.sh \
#     --description "FASE 1: Camada de domínio" \
#     --start "2026-01-14T14:00:00Z" \
#     --end "2026-01-14T16:00:00Z" \
#     --work-item-id 1234 \
#     [--activity-type "Desenvolvimento"] \
#     [--dry-run]
#
# Activity types: Desenvolvimento (default), Operação, Reunião,
#                 Rituais Scrum, Planejamento, Homologação, Treinamento
#
# AUTH (em ordem de preferência):
#   1. Variáveis de ambiente já exportadas no shell:
#        SEVENPACE_API_TOKEN, SEVENPACE_BASE_URL (recomendado).
#      Token NUNCA passa pelo AI/scripts intermediários.
#      Setup via skill `setup-7pace` que oferece macOS Keychain,
#      1Password, Bitwarden ou direto em ~/.zshrc.
#
#   2. (Legacy) Arquivo .claude/integrations/timetracking/.env
#      Mantido pra retrocompat — recomendado migrar pra opção 1.
# ============================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Parse argumentos ---
DESCRIPTION=""
START_TIME=""
END_TIME=""
WORK_ITEM_ID=""
ACTIVITY_TYPE="Desenvolvimento"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --description) DESCRIPTION="$2"; shift 2 ;;
    --start) START_TIME="$2"; shift 2 ;;
    --end) END_TIME="$2"; shift 2 ;;
    --work-item-id) WORK_ITEM_ID="$2"; shift 2 ;;
    --activity-type) ACTIVITY_TYPE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "Argumento desconhecido: $1" >&2; exit 1 ;;
  esac
done

# Validação
if [[ -z "$DESCRIPTION" || -z "$START_TIME" || -z "$END_TIME" ]]; then
  echo "ERRO: --description, --start e --end são obrigatórios." >&2
  exit 1
fi
if [[ -z "$WORK_ITEM_ID" ]]; then
  echo "ERRO: --work-item-id é obrigatório para 7pace." >&2
  exit 1
fi
if [[ ! "$WORK_ITEM_ID" =~ ^[0-9]+$ ]]; then
  echo "ERRO: --work-item-id deve conter só dígitos (ex: 1234)." >&2
  echo "  --work-item-id: '$WORK_ITEM_ID'" >&2
  exit 1
fi
ISO_Z_REGEX='^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$'
if [[ ! "$START_TIME" =~ $ISO_Z_REGEX || ! "$END_TIME" =~ $ISO_Z_REGEX ]]; then
  echo "ERRO: --start e --end devem estar no formato exato AAAA-MM-DDTHH:MM:SSZ (ex: 2026-01-14T14:00:00Z)." >&2
  echo "  --start: '$START_TIME'" >&2
  echo "  --end:   '$END_TIME'" >&2
  exit 1
fi

# --- Calcular duração em segundos ---
# Tenta BSD date (macOS) primeiro; fallback pra GNU date (Linux). Se ambos falharem,
# a string passada não está no formato esperado — encerrar com erro claro.
START_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${START_TIME%Z}" "+%s" 2>/dev/null || date -d "${START_TIME}" "+%s" 2>/dev/null || true)
END_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${END_TIME%Z}" "+%s" 2>/dev/null || date -d "${END_TIME}" "+%s" 2>/dev/null || true)
if [[ -z "$START_EPOCH" || -z "$END_EPOCH" ]]; then
  echo "ERRO: --start ou --end em formato inválido. Esperado ISO 8601 com sufixo Z (ex: 2026-01-14T14:00:00Z)." >&2
  echo "  --start: '$START_TIME'" >&2
  echo "  --end:   '$END_TIME'" >&2
  exit 1
fi
DURATION_SECONDS=$((END_EPOCH - START_EPOCH))
if (( DURATION_SECONDS <= 0 )); then
  echo "ERRO: duração inválida ($DURATION_SECONDS s) — --end deve ser posterior a --start." >&2
  exit 1
fi

# --- Activity Type IDs ---
# Os IDs abaixo são específicos do SEU tenant 7pace. Obtenha-os via API:
#   curl -s -H "Authorization: Bearer $SEVENPACE_API_TOKEN" \
#     "$SEVENPACE_BASE_URL/api/rest/activityTypes?api-version=3.2" | python3 -m json.tool
# Em seguida, substitua os placeholders abaixo. Os nomes são exemplos comuns —
# ajuste à taxonomia de atividades do seu time.
case "$ACTIVITY_TYPE" in
  "Operação") ACTIVITY_TYPE_ID="<7PACE_ACTIVITY_ID_OPERACAO>" ;;
  "Reunião") ACTIVITY_TYPE_ID="<7PACE_ACTIVITY_ID_REUNIAO>" ;;
  "Rituais Scrum") ACTIVITY_TYPE_ID="<7PACE_ACTIVITY_ID_RITUAIS_SCRUM>" ;;
  "Planejamento") ACTIVITY_TYPE_ID="<7PACE_ACTIVITY_ID_PLANEJAMENTO>" ;;
  "Homologação") ACTIVITY_TYPE_ID="<7PACE_ACTIVITY_ID_HOMOLOGACAO>" ;;
  "Treinamento") ACTIVITY_TYPE_ID="<7PACE_ACTIVITY_ID_TREINAMENTO>" ;;
  *) ACTIVITY_TYPE_ID="<7PACE_ACTIVITY_ID_DESENVOLVIMENTO>" ;;
esac

echo "=== Sync Time Entry ==="
echo "  Descrição:     $DESCRIPTION"
echo "  Início:        $START_TIME"
echo "  Fim:           $END_TIME"
echo "  Duração:       $((DURATION_SECONDS / 3600))h $((DURATION_SECONDS % 3600 / 60))min"
echo "  Work Item:     $WORK_ITEM_ID"
echo "  Activity Type: $ACTIVITY_TYPE ($ACTIVITY_TYPE_ID)"
echo ""

# ============================================================
# 7PACE TIMETRACKER
# ============================================================
if ! $DRY_RUN; then
  # Preferir env vars já exportadas; só carregar .env legado se nada estiver setado
  if [[ -z "${SEVENPACE_API_TOKEN:-}" ]] && [[ -f "$PROJECT_ROOT/.claude/integrations/timetracking/.env" ]]; then
    set -a
    source "$PROJECT_ROOT/.claude/integrations/timetracking/.env"
    set +a
  fi

  if [[ -z "${SEVENPACE_API_TOKEN:-}" ]]; then
    echo "[7pace] ERRO — SEVENPACE_API_TOKEN não configurado." >&2
    echo "  Recomendado: rode a skill /setup-7pace que oferece macOS Keychain," >&2
    echo "  1Password, Bitwarden ou export direto em ~/.zshrc (token nunca passa pelo AI)." >&2
    echo "  Alternativa rápida (não-segura): export SEVENPACE_API_TOKEN='seu-token'." >&2
    exit 1
  fi

  SEVENPACE_BASE_URL="${SEVENPACE_BASE_URL:-https://<SEVENPACE_ORG>.timehub.7pace.com}"
fi

BODY=$(WORK_ITEM_ID="$WORK_ITEM_ID" DURATION_SECONDS="$DURATION_SECONDS" \
  START_TIME="$START_TIME" DESCRIPTION="$DESCRIPTION" ACTIVITY_TYPE_ID="$ACTIVITY_TYPE_ID" \
  python3 -c '
import json, os
body = {
    "workItemId": int(os.environ["WORK_ITEM_ID"]),
    "length": int(os.environ["DURATION_SECONDS"]),
    "timestamp": os.environ["START_TIME"],
    "comment": os.environ["DESCRIPTION"],
    "activityTypeId": os.environ["ACTIVITY_TYPE_ID"],
    "timeZone": -180,
}
print(json.dumps(body))
')

if $DRY_RUN; then
  echo "[7pace] DRY RUN — POST /api/rest/workLogs?api-version=3.2"
  echo "$BODY" | python3 -m json.tool
else
  RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer $SEVENPACE_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$BODY" \
    "$SEVENPACE_BASE_URL/api/rest/workLogs?api-version=3.2")

  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

  if [[ "$HTTP_CODE" == "200" || "$HTTP_CODE" == "201" ]]; then
    ENTRY_ID=$(echo "$RESPONSE_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('id',''))" 2>/dev/null)
    if [[ -n "$ENTRY_ID" ]]; then
      echo "[7pace] OK — worklog criado (ID: $ENTRY_ID)"
    else
      # HTTP 2xx mas o payload não veio com data.id — algo mudou na API ou o formato é inesperado.
      echo "[7pace] AVISO — HTTP $HTTP_CODE mas não foi possível extrair o ID do worklog." >&2
      echo "[7pace] Resposta: $RESPONSE_BODY" >&2
      exit 1
    fi
  else
    echo "[7pace] ERRO $HTTP_CODE — $RESPONSE_BODY" >&2
    exit 1
  fi
fi

echo ""
echo "=== Sync concluído ==="
