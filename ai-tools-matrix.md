# AI Tools Matrix

> Mapeamento de convenções por ferramenta de AI suportada pelo kit.
> Os processos canonicais em `processes/` são tool-neutral; cada ferramenta tem seu wrapper apontando para eles.

---

## Ferramentas suportadas

| Ferramenta            | Local dos wrappers                       | Formato                              | Convenção de descoberta             |
| --------------------- | ---------------------------------------- | ------------------------------------ | ----------------------------------- |
| **Claude Code**       | `.claude/skills/<name>/SKILL.md`         | Markdown + frontmatter Claude        | `Skill` tool (auto-loaded)          |
| **Cursor**            | `.cursor/rules/<name>.mdc`               | MDC + frontmatter Cursor             | Agent Requested rules               |
| **Codex (OpenAI)**    | `AGENTS.md` (raiz)                       | Markdown único listando processos    | `AGENTS.md` na raiz do repo         |
| **Antigravity (Google)** | `AGENTS.md` (mesmo do Codex)          | Markdown único                       | `AGENTS.md` na raiz                 |
| **VSCode + Copilot**  | `.github/copilot-instructions.md`        | Markdown único (instructions globais)| `.github/copilot-instructions.md`   |

---

## Como cada ferramenta encontra os processos

### Claude Code
- Lê `.claude/skills/<name>/SKILL.md` automaticamente quando inicia
- Cada SKILL.md tem frontmatter `name`, `description`, `model` (opcional)
- Body do SKILL.md aponta para o canonical: `Follow [processes/<name>.md](...)`
- Invocação pelo usuário: `/<name>` (slash command) ou via tool `Skill`

### Cursor
- Lê `.cursor/rules/*.mdc` automaticamente
- Frontmatter: `description` (decide quando ativar), `globs` (opcional), `alwaysApply` (default false)
- Body aponta para o canonical
- Invocação: agente decide com base na `description` (Agent Requested) ou usuário menciona explicitamente

### Codex / Antigravity
- Lêem `AGENTS.md` na raiz do projeto na inicialização
- Conteúdo é tratado como instructions de sistema persistentes
- Lista todos os processos com link para o canonical de cada um
- Invocação: usuário pede pelo nome (ex: "siga o processo `create-work-item`")

### VSCode + Copilot
- Lê `.github/copilot-instructions.md` quando GitHub Copilot Chat é aberto
- Conteúdo é instruction global aplicada a todas as conversas
- Lista os processos disponíveis com link para o canonical
- Invocação: usuário menciona o processo no prompt

---

## Mapeamento de tool calls — Azure DevOps MCP

Os processos canonicais usam exemplos com nomes do MCP do Claude Code. Equivalentes em outras ferramentas:

| Operação                         | Claude Code (MCP)                                | Cursor / Codex / Copilot (MCP)               | Alternativas (sem MCP)                     |
| -------------------------------- | ------------------------------------------------ | -------------------------------------------- | ------------------------------------------ |
| Criar work item                  | `mcp__azure-devops__wit_create_work_item`        | Mesmo nome ou variação por adapter           | `az boards work-item create` (Azure CLI)   |
| Atualizar work item              | `mcp__azure-devops__wit_update_work_item`        | Mesmo nome                                   | `az boards work-item update`               |
| Buscar work item por ID          | `mcp__azure-devops__wit_get_work_item`           | Mesmo nome                                   | `az boards work-item show --id N`          |
| Vincular pai-filho               | `mcp__azure-devops__wit_add_child_work_items`    | Mesmo nome                                   | `az boards work-item relation add`         |
| Listar work items via WIQL       | `mcp__azure-devops__wit_query_by_wiql`           | Mesmo nome                                   | `az boards query --wiql "..."`             |
| Criar PR                         | `mcp__azure-devops__repo_create_pull_request`    | Mesmo nome                                   | `az repos pr create`                       |

Os nomes exatos dos tools no MCP variam ligeiramente entre ferramentas (alguns adicionam prefixos diferentes). Use o tool listing da sua ferramenta para confirmar nomes exatos. Para o setup do MCP em si, ver `processes/setup-azure-mcp.md` que linka a doc oficial da Microsoft cobrindo todas as ferramentas.

---

## Mapeamento de tool calls — Jira / Atlassian MCP (alternativa ao Azure DevOps)

Se o tracker for Jira (ver `processes/setup-jira.md`), troque as chamadas de Azure DevOps pelas do MCP Atlassian. Diferença conceitual: Azure move o cartão por **coluna** (`System.BoardColumn`); Jira executa **transições de workflow**.

| Operação              | Azure DevOps (MCP)              | Jira / Atlassian (MCP)                | Alternativa (CLI/REST)        |
| --------------------- | ------------------------------- | ------------------------------------- | ----------------------------- |
| Criar item            | `wit_create_work_item`          | `createJiraIssue`                     | `jira issue create` / REST    |
| Atualizar item        | `wit_update_work_item`          | `editJiraIssue`                       | REST `PUT /issue/{key}`       |
| Mover estado/coluna   | update `System.BoardColumn`     | **transição** (`transitionJiraIssue`) | REST `POST /transitions`      |
| Vincular pai-filho    | `wit_add_child_work_items`      | `createIssueLink` (epic/issue link)   | REST `POST /issueLink`        |
| Consultar             | `wit_query_by_wiql` (WIQL)      | **JQL** (`searchJiraIssuesUsingJql`)  | REST `GET /search?jql=`       |
| Comentar              | `wit_add_work_item_comment`     | `addCommentToJiraIssue`               | REST `POST /comment`          |

O MCP oficial da Atlassian também cobre **Confluence** — útil para o destino de docs externo (ver `processes/docs-target.md`).

---

## Mapeamento de tool calls — SonarQube MCP

| Operação                         | Claude Code (MCP)                                  | Cursor / Codex / Copilot (MCP)    |
| -------------------------------- | -------------------------------------------------- | --------------------------------- |
| Listar projetos                  | `mcp__sonarqube__search_my_sonarqube_projects`     | Mesmo nome ou variação            |
| Analisar arquivo                 | `mcp__sonarqube__analyze_code_snippet`             | Mesmo nome                        |
| Buscar issues                    | `mcp__sonarqube__search_sonar_issues_in_projects`  | Mesmo nome                        |
| Métricas de cobertura            | `mcp__sonarqube__get_component_measures`           | Mesmo nome                        |

Setup do MCP em `processes/setup-sonarqube-mcp.md`.

---

## Mapeamento de tool calls — Figma MCP

Para `processes/figma-requirements.md`. Três variantes de servidor (ver o processo): **Dev Mode local**, **MCP hospedado oficial** e **community REST**.

| Operação                  | Figma Dev Mode (local/oficial)   | Community REST (ex. framelink)  |
| ------------------------- | -------------------------------- | ------------------------------- |
| Código da seleção/nó      | `get_code`                       | `get_figma_data` (estrutura)    |
| Imagem/screenshot         | `get_image` / `get_screenshot`   | `download_figma_images`         |
| Variáveis/tokens          | `get_variable_defs`              | (derivar de `get_figma_data`)   |
| Metadados/estrutura       | `get_metadata`                   | `get_figma_data`                |

No Claude Code os nomes ficam `mcp__figma-dev-mode__*` ou `mcp__figma__*` conforme o servidor registrado.

---

## Convenções equivalentes — sub-agents / sub-tasks

Vários processos sugerem "delegar para subagente". Equivalência por ferramenta:

| Ferramenta            | Mecanismo equivalente                                                                  |
| --------------------- | -------------------------------------------------------------------------------------- |
| **Claude Code**       | Tool `Agent` com `subagent_type` (`general-purpose`, `Explore`, etc.) + skill `subagent-driven-development` |
| **Cursor**            | Cursor Agents (Background Agents) ou sub-prompts em chat separado                      |
| **Codex / Antigravity**| Sub-task tool ou worktree paralelo (depende da ferramenta)                            |
| **VSCode + Copilot**  | Não há sub-agentes nativos — executar diretamente                                       |

Quando o canonical menciona "despachar subagente", adapte para o mecanismo da sua ferramenta. Se não houver, execute na sessão principal.

---

## Convenções equivalentes — memória persistente

Para processos que pedem "salvar na memória" (ex: Projeto/Área default do Azure DevOps):

| Ferramenta            | Mecanismo equivalente                                                                  |
| --------------------- | -------------------------------------------------------------------------------------- |
| **Claude Code**       | Auto-memory em `~/.claude/projects/<project>/memory/` (ver instruções do system prompt)|
| **Cursor**            | Adicionar a `.cursor/rules/<context>.mdc` com `alwaysApply: true`                       |
| **Codex / Antigravity**| Editar `AGENTS.md` adicionando a seção de contexto                                    |
| **VSCode + Copilot**  | Editar `.github/copilot-instructions.md`                                                |

---

## Skills do Superpowers (multi-plataforma)

O **Superpowers** (https://github.com/obra/superpowers) é o pacote de skills de workflow (brainstorming, planning, code review, TDD, debugging, executing-plans, etc.) usado pelos processos canonicais. **Não é exclusivo do Claude Code** — suporta Claude Code, Cursor, OpenAI Codex, GitHub Copilot CLI, Gemini CLI e OpenCode.

| Ferramenta              | Comando de instalação                                                        |
| ----------------------- | ---------------------------------------------------------------------------- |
| **Claude Code**         | `/plugin install superpowers@claude-plugins-official`                        |
| **Cursor**              | `/add-plugin superpowers` no Agent chat                                      |
| **OpenAI Codex**        | Buscar via interface `/plugins`                                              |
| **GitHub Copilot CLI**  | Registrar marketplace + `copilot plugin install`                             |
| **Gemini CLI**          | `gemini extensions install` direto do repo                                   |
| **OpenCode**            | Seguir config do projeto                                                     |

Quando os processos canonicais mencionam skills `superpowers:*` (ex: `superpowers:systematic-debugging`, `superpowers:brainstorming`), elas estão disponíveis em todas as ferramentas acima após a instalação.

---

## Adicionando suporte a uma nova ferramenta

1. Documente a convenção da ferramenta neste matrix
2. Crie wrappers no formato esperado pela ferramenta apontando para os canonicais
3. Atualize/adicione o entry-point único se a ferramenta usa um (`AGENTS.md` ou similar)
