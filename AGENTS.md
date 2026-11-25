# AI Agent Instructions — o projeto

This repository supports AI-assisted development across multiple tools (Claude Code, Cursor, Codex, Antigravity, VSCode + Copilot). The processes below are **tool-neutral** and live as canonical markdown in `processes/`. Each AI tool has thin wrappers that point to these canonicals — see `ai-tools-matrix.md` for how each tool discovers and invokes them.

## Conventions

- **Source of truth:** `processes/<name>.md` (this is what every wrapper points to)
- **Wrappers per tool** (committed to the repo, no setup needed):
  - Claude Code: `.claude/skills/<name>/SKILL.md`
  - Cursor: `.cursor/rules/<name>.mdc`
  - Codex / Antigravity: this `AGENTS.md` (single file, sections below)
  - VSCode + Copilot: `.github/copilot-instructions.md`

- **Tool-call examples in canonicals**: most procedures use Claude Code MCP names (e.g., `mcp__azure-devops__wit_create_work_item`, `mcp__sonarqube__analyze_code_snippet`) as concrete examples. When working in Codex/Antigravity, use the equivalent tools from your stack:
  - For Azure DevOps: the Azure DevOps MCP from Microsoft (same MCP, different invocation per tool — see `setup-azure-mcp` and the official docs at https://github.com/microsoft/azure-devops-mcp/blob/main/docs/GETTINGSTARTED.md), or Azure CLI (`az boards`, `az repos`)
  - For SonarQube: the SonarQube MCP (Docker `mcp/sonarqube`) — see `setup-sonarqube-mcp`
  - Mapping table in `ai-tools-matrix.md`

- **Sub-agents**: when a process suggests "delegate to a sub-agent", adapt to your tool's mechanism (sub-tasks, background agents, worktree dispatching). If unavailable, execute in the main session.

## Project context

- **Project:** o projeto — stack definido via `/integrar` (exemplo do kit: Angular + Material, Clean Architecture, Vitest, Playwright)
- **Repository:** `<ORG>/<PROJECT_KEY>`
- **Tracker:** Azure DevOps por padrão nos exemplos; para Jira use `setup-jira` (os exemplos `mcp__azure-devops__*` viram chamadas do MCP Atlassian/Jira)
- **Architecture overview:** `templates/project-reference.template.md`
- **Codebase snapshot for discovery:** `docs/discovery.md` (template to fill in)
- **Workflow with AI:** `docs/workflow.md`
- **E2E testing conventions:** `docs/e2e.md`
- **Work-items process:** `docs/processo-work-items.md`

## Available processes

When the user requests one of these by name (e.g., "rode o `phase-code-review`"), open the corresponding canonical and follow it.

| Process                   | Canonical                                                                                  | Resumo                                                                                  |
| ------------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| `start-workflow`          | [processes/start-workflow.md](processes/start-workflow.md) | Ponto de entrada para nova sessão de desenvolvimento (feature/bug/refactor/freestyle)   |
| `create-work-item`        | [processes/create-work-item.md](processes/create-work-item.md) | Criar/vincular work item no Azure DevOps Board (Feature → User Story → Tasks)            |
| `spec-builder`            | [processes/spec-builder.md](processes/spec-builder.md)     | Construir especificação de feature a partir do template padrão                          |
| `phase-code-review`  | [processes/phase-code-review.md](processes/phase-code-review.md) | Code review com lint + typecheck + SonarQube + testes + correções automáticas |
| `timesync`                | [processes/timesync.md](processes/timesync.md)             | Sincronização de horas no 7pace Timetracker                                             |
| `setup-azure-mcp`         | [processes/setup-azure-mcp.md](processes/setup-azure-mcp.md) | Configurar MCP do Azure DevOps na ferramenta de AI em uso                                |
| `setup-sonarqube-mcp`     | [processes/setup-sonarqube-mcp.md](processes/setup-sonarqube-mcp.md) | Configurar MCP do SonarQube (via Docker)                                                |
| `setup-7pace`             | [processes/setup-7pace.md](processes/setup-7pace.md)       | Configurar integração com 7pace Timetracker (token + .env)                              |
| `full-setup`              | [processes/full-setup.md](processes/full-setup.md)         | Setup completo do ambiente em uma nova máquina                                          |
| `scaffold`                | [processes/scaffold.md](processes/scaffold.md)             | Bootstrap de um projeto NOVO (greenfield) com o kit pré-configurado                     |
| `integrar`                | [processes/integrar.md](processes/integrar.md)             | Adaptar o kit ao projeto host (stack, tracker, time tracking, docs, convenções)         |
| `figma-requirements`      | [processes/figma-requirements.md](processes/figma-requirements.md) | Levantar requisitos a partir de um design no Figma (MCP local ou online)                |
| `setup-jira`              | [processes/setup-jira.md](processes/setup-jira.md)         | Configurar MCP do Jira (Atlassian) — alternativa ao `setup-azure-mcp`                    |
| `docs-target`             | [processes/docs-target.md](processes/docs-target.md)       | Destino da documentação: repo ou plataforma externa (Confluence/Outline/Notion)         |

## Idioma e convenções de código

- **Idioma da UI e mensagens:** Português brasileiro (pt-BR) — todo texto de interface é hardcoded em pt-BR
- **Commit messages:** Português brasileiro
- **Sem `Co-Authored-By` em commits**
- **Standalone components, `inject()`, Angular Signals, `OnPush`**
- **Sem `fakeAsync`/`tick`, sem `TestBed.initTestEnvironment()`** — Vitest com `@angular/build:unit-test`

## Updates

Quando os canonicais em `processes/` mudam, esta `AGENTS.md` continua atual automaticamente — só os links são fixos, o conteúdo dos processos é lido em tempo real.

Quando um novo processo é adicionado, atualizar:
1. Criar canonical em `processes/<name>.md`
2. Adicionar wrappers correspondentes em `.claude/skills/<name>/SKILL.md` e `.cursor/rules/<name>.mdc`
3. Adicionar nova linha à tabela acima neste arquivo e em `.github/copilot-instructions.md`
