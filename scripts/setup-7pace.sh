#!/usr/bin/env bash
# ============================================================
# setup-7pace.sh — Configura SEVENPACE_API_TOKEN e SEVENPACE_BASE_URL
# armazenando o token de forma que ele nunca apareça no shell rc.
#
# Em macOS, oferece duas opções:
#   1. macOS Keychain — encrypted at rest. ~/.7pace contém apenas o
#      comando `security find-generic-password ...`, não o token.
#   2. Arquivo plain-text em ~/.7pace com chmod 600.
#
# Em Linux/WSL/outros: usa apenas a opção (2).
#
# Em ambos os casos o ~/.zshrc/~/.bashrc apenas dá `source ~/.7pace`,
# então mesmo que o usuário abra o rc em uma IDE com AI, a chave (ou o
# comando que a recupera) não é exposta — vive em arquivo separado que
# o usuário nunca abre.
# ============================================================

set -euo pipefail

# --- Detectar shell rc ---
detect_rc() {
  local shell_name="${SHELL##*/}"
  case "$shell_name" in
    zsh) echo "$HOME/.zshrc" ;;
    bash)
      if [[ "$(uname)" == "Darwin" ]] && [[ -f "$HOME/.bash_profile" ]]; then
        echo "$HOME/.bash_profile"
      else
        echo "$HOME/.bashrc"
      fi
      ;;
    *) echo "$HOME/.profile" ;;
  esac
}

RC_FILE="$(detect_rc)"
SECRET_FILE="$HOME/.7pace"
KEYCHAIN_SERVICE="7pace-api-token"
BASE_URL_DEFAULT="https://<SEVENPACE_ORG>.timehub.7pace.com"
IS_MACOS=false
[[ "$(uname)" == "Darwin" ]] && IS_MACOS=true

echo "🔑 Setup 7pace Timetracker"
echo ""
echo "  OS:           $(uname -s)"
echo "  Shell:        ${SHELL##*/}"
echo "  Arquivo rc:   $RC_FILE"
echo ""

# --- Escolher modo de armazenamento ---
STORAGE_MODE="file"
if $IS_MACOS; then
  echo "Detectei macOS. Onde armazenar o token?"
  echo "  1. macOS Keychain (recomendado — encrypted at rest pelo OS)"
  echo "  2. Arquivo plain-text em ~/.7pace (chmod 600)"
  echo ""
  read -r -p "Escolha [1]: " CHOICE
  CHOICE="${CHOICE:-1}"
  case "$CHOICE" in
    1) STORAGE_MODE="keychain" ;;
    2) STORAGE_MODE="file" ;;
    *) echo "✗ Escolha inválida — abortando." >&2; exit 1 ;;
  esac
  echo ""
fi

if [[ "$STORAGE_MODE" == "keychain" ]]; then
  echo "Token será armazenado no macOS Keychain (service: $KEYCHAIN_SERVICE)."
  echo "$SECRET_FILE conterá apenas o comando 'security find-generic-password',"
  echo "não o token em si."
else
  echo "Token será gravado em $SECRET_FILE (chmod 600)."
  echo "Mesmo que você abra o $(basename "$RC_FILE") em uma IDE com AI, a chave"
  echo "não é exposta — ela fica num arquivo separado que você nunca abre."
fi
echo ""

# --- Pedir token (input oculto) ---
read -r -s -p "Cole seu token do 7pace (input oculto, Enter para confirmar): " TOKEN
echo ""

if [[ -z "$TOKEN" ]]; then
  echo "✗ Token vazio — abortando." >&2
  exit 1
fi

# Confirmar base URL (default configurável via SEVENPACE_BASE_URL)
read -r -p "Base URL [$BASE_URL_DEFAULT]: " BASE_URL
BASE_URL="${BASE_URL:-$BASE_URL_DEFAULT}"

# --- Gravar segredo conforme modo ---
umask 077
case "$STORAGE_MODE" in
  keychain)
    # -U faz update se já existir; redirecionar stdout pra evitar dump do account
    if security add-generic-password -U -a "$USER" -s "$KEYCHAIN_SERVICE" -w "$TOKEN" 2>/dev/null; then
      echo "✓ Token armazenado no Keychain (service: $KEYCHAIN_SERVICE, account: $USER)"
    else
      echo "✗ Falha ao gravar no Keychain — abortando." >&2
      exit 1
    fi
    cat > "$SECRET_FILE" <<EOF
# 7pace Timetracker — token no macOS Keychain (gerado por setup-7pace.sh)
# Este arquivo NÃO contém o token: apenas o comando que o recupera.
export SEVENPACE_API_TOKEN=\$(security find-generic-password -s '$KEYCHAIN_SERVICE' -a "\$USER" -w 2>/dev/null)
export SEVENPACE_BASE_URL='$BASE_URL'
EOF
    chmod 600 "$SECRET_FILE"
    echo "✓ $SECRET_FILE gravado (referencia o Keychain, não contém o token)"
    ;;
  file)
    cat > "$SECRET_FILE" <<EOF
# 7pace Timetracker — gerado por scripts/setup-7pace.sh
# NÃO commitar. NÃO compartilhar. NÃO abrir em IDE com AI.
export SEVENPACE_API_TOKEN='$TOKEN'
export SEVENPACE_BASE_URL='$BASE_URL'
EOF
    chmod 600 "$SECRET_FILE"
    echo "✓ Token gravado em $SECRET_FILE (permissão 600)"
    ;;
esac

# Limpar variável da memória do script
TOKEN=""

# --- Adicionar source ao rc (idempotente) ---
SOURCE_LINE='[ -f "$HOME/.7pace" ] && source "$HOME/.7pace"'
if [[ -f "$RC_FILE" ]] && grep -qF '.7pace' "$RC_FILE"; then
  echo "✓ $RC_FILE já dá source no $SECRET_FILE — não duplicado"
else
  {
    echo ""
    echo "# 7pace Timetracker — configurado por setup-7pace.sh"
    echo "$SOURCE_LINE"
  } >> "$RC_FILE"
  echo "✓ Adicionada linha 'source ~/.7pace' em $RC_FILE"
fi

# --- Próximos passos ---
echo ""
echo "─────────────────────────────────────────────"
echo "Para ativar nesta sessão:"
echo "  source $RC_FILE"
echo ""
echo "Ou abra um novo terminal. Depois valide:"
echo "  [[ -n \"\$SEVENPACE_API_TOKEN\" ]] && echo OK"
echo "─────────────────────────────────────────────"
