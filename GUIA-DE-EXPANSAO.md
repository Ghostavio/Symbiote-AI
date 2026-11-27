# Guia de Expansão — Trocar e Adicionar Ferramentas

Como adaptar o kit a outras ferramentas: **Jira no lugar de Azure DevOps**, **Toggl/Harvest no lugar de 7pace**, **Confluence/Outline no lugar de docs no repo**, e como **adicionar uma nova ferramenta de IA** ou uma **skill nova**.

> **Atalho:** a skill **`simbiose`** automatiza a maior parte deste guia (detecta o contexto e adaptadores compatíveis, propõe um plano e adapta os arquivos com sua confirmação). Use este documento para entender o que ela faz — ou para ajustes manuais.

## Modelo mental

Tudo gira em torno de 4 peças:

1. **Processos canônicos** (`processes/*.md`) — a lógica, neutra de ferramenta. **Raramente mudam.**
2. **Wrappers por ferramenta de IA** (`.agents/skills/`, `.claude/skills/`, `.cursor/rules/`, `AGENTS.md`, `GEMINI.md`, `.github/copilot-instructions.md`) — apontadores finos.
3. **`ai-tools-matrix.md`** — tabela de equivalência de tool-calls de MCP entre ferramentas.
4. **Placeholders** (`<AZURE_ORG>`, `<PROJECT_KEY>`, `<TEST_CMD>`, `<src>`, …) — o que é específico do projeto.

Expandir = mexer em (2), (3) e nos placeholders — quase nunca na lógica (1).

---

## Receita A — Azure DevOps → Jira

1. **MCP:** rode `/setup-jira` (ou siga [`processes/setup-jira.md`](processes/setup-jira.md)). Opção A = MCP oficial da Atlassian (OAuth, cobre Jira **e** Confluence); Opção B = `mcp-atlassian` com API token (Cloud ou Server/DC).
2. **Skills:** mantenha `setup-jira` e remova/ignore `setup-azure-mcp` dos wrappers (ou deixe ambos como referência).
3. **Tool-calls:** na `ai-tools-matrix.md` (seção *Jira / Atlassian MCP*) os processos passam a usar:
   - criar item → `createJiraIssue` (em vez de `wit_create_work_item`)
   - consultar → **JQL** `searchJiraIssuesUsingJql` (em vez de WIQL)
   - **mover de coluna → transição de workflow** `transitionJiraIssue` (Jira não tem "coluna livre" como o Azure)
4. **Fluxos:** em [`processes/start-workflow.md`](processes/start-workflow.md), os passos "mover a US para `Waiting PR Approve`" (que no Azure alteram `System.BoardColumn`) viram a **transição** equivalente do seu workflow Jira (ex.: "In Review"). Em [`processes/create-work-item.md`](processes/create-work-item.md), Feature→User Story→Tasks viram Epic→Story→Sub-task.
5. **Env:** `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN` (Opção B) — sempre de variável de ambiente.

> O mesmo MCP oficial da Atlassian habilita publicar docs no **Confluence** (ver Receita C).

---

## Receita B — 7pace → Toggl / Clockify / Harvest

O contrato dos scripts é comum (`--description --start --end [--work-item-id] [--dry-run]`). Gere um `scripts/sync-<tool>.sh` análogo ao `scripts/sync-7pace.sh`, lendo credenciais de env:

| Ferramenta | Auth | Endpoint | Env |
|---|---|---|---|
| Toggl Track | Basic `{token}:api_token` | `POST https://api.track.toggl.com/api/v9/workspaces/{wsId}/time_entries` | `TOGGL_API_TOKEN`, `TOGGL_WORKSPACE_ID`, `TOGGL_PROJECT_ID` |
| Clockify | `X-Api-Key` | `POST https://api.clockify.me/api/v1/workspaces/{wsId}/time-entries` | `CLOCKIFY_API_TOKEN`, `CLOCKIFY_WORKSPACE_ID`, `CLOCKIFY_PROJECT_ID` |
| Harvest | `Bearer` + `Harvest-Account-Id` | `POST https://api.harvestapp.com/v2/time_entries` | `HARVEST_API_TOKEN`, `HARVEST_ACCOUNT_ID`, `HARVEST_PROJECT_ID`, `HARVEST_TASK_ID` |

Passos: copie `sync-7pace.sh`/`sync-clockify.sh` como molde → ajuste auth/endpoint/payload → atualize `processes/timesync.md` com os exemplos da ferramenta → se houver MCP, adicione à matrix. (Clockify já vem pronto em `.claude/integrations/timetracking/`.)

> **Adaptador candidato (Jira):** [Tempo Timesheets for Jira](https://marketplace.atlassian.com/apps/6572/timesheets-by-tempo-jira-time-tracking?hosting=cloud&tab=overview) está listado como candidato no kit para times que usam Jira, até que uma integração verificada seja entregue.

---

## Receita C — Docs no repo → plataforma externa (PRs limpos)

Siga [`processes/docs-target.md`](processes/docs-target.md):

1. Defina `DOC_TARGET=confluence|outline|notion`.
2. **Confluence:** use o MCP oficial da Atlassian (`createConfluencePage`/`updateConfluencePage`) no espaço `CONFLUENCE_SPACE_KEY`. **Outline:** API REST (`documents.create`). **Notion:** MCP/ API do Notion.
3. Os fluxos passam a **publicar** discovery/design/diário/post-mortem na plataforma e a referenciar a **URL** no work item e no PR — nenhum `.md` de processo é commitado.

---

## Receita D — SonarQube → outro / nenhum

- **Nenhum:** remova o passo 8 (SonarQube) de [`processes/phase-code-review.md`](processes/phase-code-review.md) e a skill `setup-sonarqube-mcp` dos wrappers.
- **Outro linter/qualidade:** troque a chamada `mcp__sonarqube__analyze_code_snippet` pela ferramenta equivalente e ajuste `<PROJECT_KEY>`.

---

## Receita E — Adicionar uma nova ferramenta de IA (ex.: Gemini CLI, Windsurf)

1. Descubra a convenção de descoberta da ferramenta (arquivo/diretório que ela lê).
2. Crie os **wrappers** nesse formato, apontando para `processes/<name>.md` (não duplique conteúdo).
3. Adicione uma linha à tabela *Ferramentas suportadas* em `ai-tools-matrix.md` e, se a ferramenta usa um entry-point único (como `AGENTS.md`), liste os processos lá.
4. Mapeie os nomes de tool-call de MCP da ferramenta nas seções da matrix.
5. Instale o **Superpowers** na ferramenta (a matrix lista o comando por ferramenta).

---

## Receita F — Adicionar uma skill/processo novo

1. Crie o canônico `processes/<name>.md` (com frontmatter `name`/`description`).
2. Crie os wrappers: `.agents/skills/<name>/SKILL.md`, `.claude/skills/<name>/SKILL.md` e `.cursor/rules/<name>.mdc` (apontando para o canônico).
3. Adicione a linha à tabela de processos em `AGENTS.md` **e** em `.github/copilot-instructions.md`.
4. Se a skill usa um MCP, documente os tool-calls em `ai-tools-matrix.md`.

---

## Receita G — Adicionar um novo adaptador (stack, cloud ou observabilidade)

Para especializar o kit para uma tecnologia (ex.: React, Cloudflare, AWS, OpenTelemetry) sem acoplar o core neutro, siga o contrato em `adapters/README.md` (no repositório do kit):

1. Crie a pasta `adapters/<categoria_dir>/<id>/`, onde `<categoria_dir>` é `stacks`, `cloud` ou `observability`.
2. Crie `adapter.json` com `id`, `name`, `category`, `description`, sinais `detect` (`files`, `packages` ou `directories`), `commands` opcionais e mapa `files` (`conventions`, `review_checks`, e opcionais `editor_settings`/`skills`).
3. Escreva `conventions.md` (convenções para `.claude/PROJECT_REFERENCE.md`) e `review-checks.md` (checks para `phase-code-review`).
4. Valide o manifesto e links com `python3 -B scripts/validate-kit.py` e `python3 -B -m unittest discover -s tests -v`.

---

## Checklist pós-expansão

- [ ] Nenhum `<PLACEHOLDER>` sobrou onde deveria ter valor real (`grep -rnE '<[A-Z0-9_]+>|<src>|<e2e-dir>' .`).
- [ ] `.env.example` atualizado com as novas chaves; `.env` no `.gitignore`.
- [ ] Wrappers das ferramentas em uso apontam todos para `processes/`.
- [ ] `ai-tools-matrix.md` reflete os MCPs reais.
- [ ] Um fluxo end-to-end testado (ex.: `start-workflow` → Express → PR).
