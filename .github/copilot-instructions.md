# GitHub Copilot Instructions — o projeto

This repository supports AI-assisted development across multiple tools. The processes below are **tool-neutral** and live as canonical markdown in `processes/`. See `ai-tools-matrix.md` for cross-tool conventions.

## Project context

- **Project:** o projeto — stack definido via `/integrar` (exemplo do kit: Angular + Material, Clean Architecture, Vitest, Playwright)
- **Repository:** `<ORG>/<PROJECT_KEY>`
- **Tracker:** Azure DevOps nos exemplos; para Jira use `setup-jira`
- **Architecture overview:** `templates/project-reference.template.md`
- **Codebase snapshot for discovery:** `docs/discovery.md` (template to fill in)
- **Workflow with AI:** `docs/workflow.md`
- **E2E testing conventions:** `docs/e2e.md`
- **Work-items process:** `docs/processo-work-items.md`

## Tool-call examples in canonicals

Most processes use Claude Code MCP names (e.g., `mcp__azure-devops__wit_create_work_item`, `mcp__sonarqube__analyze_code_snippet`) as concrete examples. In VSCode + Copilot, use the equivalent MCP tools registered in your `settings.json` under `github.copilot.chat.mcp.servers` — typically the same MCP servers (Azure DevOps, SonarQube), just invoked through Copilot's tool layer. See `ai-tools-matrix.md` for the mapping table.

## Available processes

When the user requests one of these by name, open the corresponding canonical and follow it.

| Process                   | Canonical                                                                                  | Resumo                                                                                  |
| ------------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| `start-workflow`          | [processes/start-workflow.md](../processes/start-workflow.md) | Ponto de entrada para nova sessão de desenvolvimento                                    |
| `create-work-item`        | [processes/create-work-item.md](../processes/create-work-item.md) | Criar/vincular work item no Azure DevOps Board                                          |
| `spec-builder`            | [processes/spec-builder.md](../processes/spec-builder.md)     | Construir especificação de feature                                                       |
| `phase-code-review`  | [processes/phase-code-review.md](../processes/phase-code-review.md) | Code review com lint + typecheck + SonarQube + testes                                  |
| `timesync`                | [processes/timesync.md](../processes/timesync.md)             | Sincronização de horas no 7pace Timetracker                                             |
| `timesync-clockify`       | [processes/timesync-clockify.md](../processes/timesync-clockify.md) | Extensão opcional para registrar as mesmas horas também no Clockify                     |
| `setup-azure-mcp`         | [processes/setup-azure-mcp.md](../processes/setup-azure-mcp.md) | Configurar MCP do Azure DevOps                                                           |
| `setup-sonarqube-mcp`     | [processes/setup-sonarqube-mcp.md](../processes/setup-sonarqube-mcp.md) | Configurar MCP do SonarQube (via Docker)                                                |
| `setup-7pace`             | [processes/setup-7pace.md](../processes/setup-7pace.md)       | Configurar integração com 7pace Timetracker                                             |
| `full-setup`              | [processes/full-setup.md](../processes/full-setup.md)         | Setup completo do ambiente em uma nova máquina                                          |
| `scaffold`                | [processes/scaffold.md](../processes/scaffold.md)             | Bootstrap de um projeto NOVO (greenfield) com o kit pré-configurado                     |
| `integrar`                | [processes/integrar.md](../processes/integrar.md)             | Adaptar o kit ao projeto host (stack, tracker, time tracking, docs, convenções)         |
| `figma-requirements`      | [processes/figma-requirements.md](../processes/figma-requirements.md) | Levantar requisitos a partir de um design no Figma (MCP local ou online)        |
| `setup-jira`              | [processes/setup-jira.md](../processes/setup-jira.md)         | Configurar MCP do Jira (Atlassian) — alternativa ao `setup-azure-mcp`                    |
| `docs-target`             | [processes/docs-target.md](../processes/docs-target.md)       | Destino da documentação: repo ou plataforma externa (Confluence/Outline/Notion)         |

## Idioma e convenções de código

- **Idioma da UI e mensagens:** Português brasileiro (pt-BR)
- **Commit messages:** Português brasileiro
- **Sem `Co-Authored-By` em commits**
- **Standalone components, `inject()`, Angular Signals, `OnPush`**
- **Sem `fakeAsync`/`tick`, sem `TestBed.initTestEnvironment()`** — Vitest com `@angular/build:unit-test`
