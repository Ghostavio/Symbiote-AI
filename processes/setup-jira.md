---
name: setup-jira
description: "Use quando o tracker do projeto for Jira (Atlassian) e o MCP Server do Jira não estiver configurado para a ferramenta de IA em uso (Claude Code, Cursor, Codex, VSCode/Copilot, etc.). Alternativa ao setup-azure-mcp para times que usam Jira."
---

# Setup Jira (Atlassian) MCP

Configura o acesso a **Jira** (e, de quebra, **Confluence**) via MCP, para que o assistente crie/atualize issues, faça transições, vincule itens e consulte via JQL — o equivalente Jira do `setup-azure-mcp`. Escolha **uma** das opções.

> **Por que importa:** com o MCP do Jira, as skills `create-work-item` e `start-workflow` passam a criar/mover issues no Jira em vez de work items no Azure DevOps. Se você usa Confluence para documentação, o mesmo MCP oficial (Opção A) cobre o destino de docs externo — ver [`docs-target.md`](docs-target.md).

## Opção A — Atlassian Remote MCP (oficial, OAuth) — recomendado para Cloud

Servidor hospedado pela Atlassian (Rovo MCP), cobre **Jira + Confluence**, autenticação OAuth (sem token em arquivo).

- **Endpoint:** `https://mcp.atlassian.com/v1/sse`
- **Claude Code:**
  ```bash
  claude mcp add --transport sse atlassian https://mcp.atlassian.com/v1/sse
  # depois rode /mcp e autentique no navegador (OAuth)
  ```
- **Cursor / Codex / Copilot:** registre o mesmo endpoint SSE na configuração de MCP da ferramenta e autentique via OAuth.
- **`.mcp.json` (genérico):**
  ```json
  { "mcpServers": { "atlassian": { "type": "sse", "url": "https://mcp.atlassian.com/v1/sse" } } }
  ```
- **Antigravity (`~/.gemini/config/mcp_config.json`):** o Antigravity suporta **Stdio** e **Streamable HTTP** (`/mcp`), não HTTP+SSE legado (`/sse`) diretamente. Use o endpoint Streamable HTTP quando disponível ou o bridge Stdio `mcp-remote`:
  ```json
  { "mcpServers": { "atlassian": { "command": "npx", "args": ["-y", "mcp-remote", "https://mcp.atlassian.com/v1/sse"] } } }
  ```

## Opção B — `mcp-atlassian` (community, API token) — Cloud ou Server/Data Center

Servidor local (roda via `uvx`/Docker), usa **API token**. Útil para Jira Server/Data Center on-premise ou quando OAuth não é viável.

1. Gere um **API token**: https://id.atlassian.com/manage-profile/security/api-tokens (Cloud) ou um Personal Access Token (Server/DC).
2. Variáveis de ambiente (NUNCA hardcode o token):
   ```bash
   JIRA_URL=https://<SEU_SITE>.atlassian.net      # ou a URL do seu Jira Server/DC
   JIRA_USERNAME=<seu-email>                       # Cloud
   JIRA_API_TOKEN=<seu-token>                      # do ambiente/secret manager
   # Confluence (opcional): CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN
   ```
3. `.mcp.json` (genérico, via Docker):
   ```json
   { "mcpServers": { "jira": {
       "command": "docker",
       "args": ["run","-i","--rm",
         "-e","JIRA_URL","-e","JIRA_USERNAME","-e","JIRA_API_TOKEN",
         "ghcr.io/sooperset/mcp-atlassian:latest"]
   } } }
   ```
   (ou `uvx mcp-atlassian` conforme a doc do projeto). Passe as variáveis pelo ambiente do processo.

## Verificação

Peça ao assistente para listar projetos/issues (ex.: "liste meus issues abertos no projeto X"). Se responder com dados reais do Jira, está configurado. No Claude Code, `/mcp` mostra o servidor `atlassian`/`jira` como conectado.

## Mapeamento de operações (Azure DevOps → Jira)

Use ao adaptar `create-work-item`/`start-workflow` (ver `ai-tools-matrix.md` e `GUIA-DE-EXPANSAO.md`):

| Operação | Azure DevOps (MCP) | Jira (MCP / equivalente) |
|---|---|---|
| Criar item | `wit_create_work_item` | criar issue (`createJiraIssue` / `jira_create_issue`) |
| Atualizar item | `wit_update_work_item` | editar issue (`editJiraIssue` / `jira_update_issue`) |
| Mover de coluna/estado | update `System.BoardColumn` | **transição** (`transitionJiraIssue`) — Jira usa workflow/transitions, não coluna livre |
| Vincular pai-filho | `wit_add_child_work_items` | issue link / epic link (`createIssueLink`) |
| Consultar | `wit_query_by_wiql` (WIQL) | **JQL** (`searchJiraIssuesUsingJql`) |
| Comentar | `wit_add_work_item_comment` | `addCommentToJiraIssue` |

> Diferença conceitual importante: no Azure você move um cartão entre colunas do board (`System.BoardColumn`); no Jira você executa uma **transição de workflow** (ex.: "In Review"), que pode ter condições/validações. Ajuste os passos "mover para Waiting PR Approve" dos fluxos do `start-workflow` para a transição equivalente do seu workflow Jira.

## Próximos passos

- Atualize a `ai-tools-matrix.md` (seção de tool-calls do tracker) com os nomes reais do MCP do Jira na sua ferramenta.
- Rode `integrar` se ainda não rodou — ele troca `setup-azure-mcp`↔`setup-jira` e ajusta os fluxos automaticamente.
