# Integração Clockify — Wrapper para timetracking duplo

Integração **opcional** para quem precisa registrar horas no **Clockify** (ex.: uma consultoria que cobra por hora) simultaneamente ao **7pace** (timetracking principal do time). O wrapper `sync.sh` chama o `scripts/sync-7pace.sh` e o `sync-clockify.sh` local numa única invocação.

> **Não commite o `.env`.** Cada dev preenche o seu com as próprias credenciais. O `.env` está fora do pacote por segurança — use o `.env.example` desta pasta (as mesmas chaves da seção 2 abaixo) como base.

## Arquivos desta pasta

```
.claude/integrations/timetracking/
  .env.example      ← modelo do .env (copie para .env e preencha)
  .env              ← suas credenciais (criar a partir do .env.example)
  sync.sh           ← wrapper: registra em 7pace + Clockify
  sync-clockify.sh  ← registra no Clockify (chamado pelo wrapper)
  README.md         ← este arquivo
```

## Setup (5 minutos)

### 1. (Opcional) Clockify MCP Server — para uso direto via assistente de IA

```bash
mkdir -p .claude/integrations/clockify-mcp
cd .claude/integrations/clockify-mcp
git clone https://github.com/https-eduardo/clockify-mcp-server.git .
npm install
```

Adicionar ao `~/.claude.json` (ou ao `.mcp.json` do projeto), na seção `mcpServers`:
```json
"clockify": {
  "type": "stdio",
  "command": "tsx",
  "args": ["/CAMINHO_ABSOLUTO/.claude/integrations/clockify-mcp/src/index.ts", "--local"],
  "env": { "CLOCKIFY_API_TOKEN": "SEU_TOKEN_AQUI" }
}
```

### 2. Preencher credenciais

Copie o `.env.example` desta pasta para `.env` e preencha (troque cada valor de exemplo abaixo pelo valor real; na URL, troque `<SEVENPACE_ORG>` e mantenha as aspas simples):

```bash
# Clockify — https://app.clockify.me/user/preferences → API → Generate
CLOCKIFY_API_TOKEN=seu_token_aqui
CLOCKIFY_WORKSPACE_ID=seu_workspace_id_aqui
CLOCKIFY_PROJECT_ID=seu_project_id_aqui
# Opcional: só para listar entradas (o sync-clockify.sh não usa)
CLOCKIFY_USER_ID=seu_user_id_aqui

# 7pace (compartilhado com scripts/sync-7pace.sh)
SEVENPACE_API_TOKEN=seu_token_7pace
SEVENPACE_BASE_URL='https://<SEVENPACE_ORG>.timehub.7pace.com'
```

**Como obter os IDs do Clockify:**
```bash
# Workspace ID
curl -s -H "X-Api-Key: SEU_TOKEN" \
  https://api.clockify.me/api/v1/workspaces \
  | python3 -c "import sys,json; [print(f'{w[\"id\"]}  {w[\"name\"]}') for w in json.load(sys.stdin)]"

# Project ID (substituir <CLOCKIFY_WORKSPACE_ID> e <CLOCKIFY_PROJECT_NAME>, o nome do projeto no Clockify)
curl -s -H "X-Api-Key: SEU_TOKEN" \
  "https://api.clockify.me/api/v1/workspaces/<CLOCKIFY_WORKSPACE_ID>/projects?name=<CLOCKIFY_PROJECT_NAME>" \
  | python3 -c "import sys,json; [print(f'{p[\"id\"]}  {p[\"name\"]}') for p in json.load(sys.stdin)]"
```

### 3. Usar

Use o wrapper `sync.sh` (nesta pasta) — registra no **7pace E no Clockify** de uma vez, com os mesmos argumentos do `sync-7pace.sh`:

```bash
./.claude/integrations/timetracking/sync.sh \
  --description "FASE 1: Camada de domínio" \
  --start "2026-01-14T14:00:00Z" \
  --end "2026-01-14T16:00:00Z" \
  --work-item-id 1234

# Dry run (não envia nada)
./.claude/integrations/timetracking/sync.sh \
  --description "Teste" \
  --start "2026-01-15T09:00:00Z" \
  --end "2026-01-15T10:00:00Z" \
  --work-item-id 1234 \
  --dry-run
```

Se você só registra no 7pace (sem Clockify), use `scripts/sync-7pace.sh` diretamente.

### 4. (Opcional) Automatizar com a memória do assistente

Salve uma preferência no seu assistente de IA para sempre usar o wrapper `sync.sh` (em vez de `sync-7pace.sh`) ao sincronizar horas. A skill `timesync-clockify` cobre esse fluxo.
