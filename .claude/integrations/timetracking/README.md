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
  --start "2026-01-14T14:00:00-03:00" \
  --end "2026-01-14T16:00:00-03:00" \
  --work-item-id 1234

# Dry run (não envia nada)
./.claude/integrations/timetracking/sync.sh \
  --description "Teste" \
  --start "2026-01-15T09:00:00-03:00" \
  --end "2026-01-15T10:00:00-03:00" \
  --work-item-id 1234 \
  --dry-run
```

Se você só registra no 7pace (sem Clockify), use `scripts/sync-7pace.sh` diretamente.

### Retomar após falha parcial

Reutilize os argumentos da sessão original e acrescente `--provider clockify` ou `--provider 7pace` para enviar somente ao provedor pendente. O wrapper mantém o prefixo do work item no Clockify e a exceção para `Daily`. Você pode combinar com `--dry-run` para conferir o payload antes do envio.

Se houve timeout, falha de rede ou resposta inconclusiva, confira no provedor se a entrada existe antes de retomar. Sem a opção `--provider`, o wrapper continua executando 7pace primeiro e só chama Clockify se o 7pace tiver sucesso. Uma retomada explícita para Clockify retorna erro se o token ou o workspace estiver ausente.

### 4. (Opcional) Automatizar com a memória do assistente

Salve uma preferência no seu assistente de IA indicando os provedores de controle de tempo ativos no projeto (ex.: somente Clockify via `sync-clockify.sh`, ou 7pace + Clockify via o wrapper `sync.sh`). A skill canônica [`timesync`](../../../processes/timesync.md) lê essa preferência automaticamente.

## Regras específicas do Clockify

1. **Prefixo `{WorkItemId}:` na descrição:** como o Clockify não tem vínculo nativo com o tracker, use `{WorkItemId}: {nome}` (ex.: `1234: Setup e Infraestrutura`). **Exceção:** a Daily é sempre apenas `Daily` (sem prefixo e sem "Scrum").
2. **Fuso explícito:** passe `--start` e `--end` com o offset local válido na data da sessão (por exemplo, `-03:00`) ou com `Z` para UTC. O script envia os instantes em UTC.
3. **`projectId` obrigatório:** configure `CLOCKIFY_PROJECT_ID` no `.env` para vincular todas as entradas ao projeto correto.
4. **Endpoints essenciais da API v1** (`https://api.clockify.me/api/v1`, header `X-Api-Key`):
   - Criar: `POST /workspaces/{workspaceId}/time-entries`
   - Listar: `GET /workspaces/{workspaceId}/user/{userId}/time-entries?start=...&end=...`
   - Atualizar: `PUT /workspaces/{workspaceId}/time-entries/{id}`
   - Deletar: `DELETE /workspaces/{workspaceId}/time-entries/{id}`

### Checklist específico do Clockify

- [ ] Cada entrada vinculada a item do tracker tem prefixo `{WorkItemId}: ` (exceto `Daily`)
- [ ] Timestamps representam o fuso pretendido (`Z` para UTC ou offset local explícito)
- [ ] `projectId` preenchido corretamente em todas as entradas
- [ ] Dailies registradas como `Daily` (sem prefixo)
