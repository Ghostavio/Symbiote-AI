---
name: integrar
description: "Depreciado. Use simbiose para aplicar o Symbiote-AI a um projeto existente."
---

# Integrar — Adaptar o Symbiote-AI ao projeto host

> A invocação direta de `/integrar` foi depreciada. Use [`/simbiose`](simbiose.md) como entrada principal. Este procedimento continua sendo o caminho de integração para projetos existentes.

Esta skill **especializa o kit genérico** para o projeto onde ele foi solto. O kit foi montado com uma arquitetura de indireção — **processos canônicos tool-neutral** (`processes/*.md`), **wrappers finos por ferramenta** (`.agents/skills/`, `.claude/skills/`, `.cursor/rules/`, `AGENTS.md`, `GEMINI.md`, `.github/copilot-instructions.md`) e a **`ai-tools-matrix.md`** — e usa **placeholders** (`<AZURE_ORG>`, `<PROJECT_KEY>`, …). O `integrar` detecta o contexto, mapeia os placeholders para valores reais e reescreve os arquivos.

## Modo de operação: interativo (detectar → plano → aplicar)

<HARD-GATE>
NUNCA reescreva arquivos sem antes apresentar o PLANO e obter confirmação explícita do usuário. Trabalhe em um repositório com git limpo (ou faça commit antes) — o git é a rede de segurança para revisar/reverter o diff.
</HARD-GATE>

## Passo 1 — Detectar o contexto do projeto

Inspecione o repositório host (sem alterar nada ainda):

- **Stack & linguagem:** `package.json`, `pom.xml`/`build.gradle`, `go.mod`, `*.csproj`, `pyproject.toml`/`requirements.txt`, `Cargo.toml`, etc.
- **Gerenciador de pacotes:** yarn/npm/pnpm/bun, maven/gradle, pip/poetry/uv, cargo…
- **Comandos:** test, lint, typecheck, build, e2e — leia `scripts` do `package.json`/Makefile/CI.
- **Layout:** monorepo? onde fica o código-fonte (`src/`), os testes, os e2e? convenção de módulos?
- **Framework de teste:** Vitest/Jest/Playwright/Cypress, JUnit, pytest, go test, xUnit…
- **VCS host:** GitHub / Azure DevOps / GitLab / Bitbucket (olhe `git remote -v`).
- **Tracker (issues):** `.azure`/Azure remoto → Azure DevOps; `.github/` issues; Jira (link no README/CI); GitLab issues.
- **Time tracking:** há scripts/menções a 7pace, Clockify, Toggl, Harvest? (default: perguntar).
- **Qualidade de código:** `sonar-project.properties` → SonarQube; ESLint/etc.
- **Plataforma de docs:** wiki do repo, Confluence, Outline, Notion? (ver Passo 2.4).
- **Instruções de IA existentes:** já há `CLAUDE.md`/`AGENTS.md`/`.cursor/rules`/`.github/copilot-instructions.md`? (fundir, não sobrescrever cegamente).
- **Adaptadores compatíveis:** compare arquivos e dependências detectados com os sinais `detect` nos manifestos `adapters/*/*/adapter.json` disponíveis no kit (ver `adapters/README.md`) para sugerir adaptadores de stack, cloud e observabilidade.

Resuma o que detectou e o que ficou incerto.

## Passo 2 — Mapear dimensões de adaptação (perguntar uma por vez o que não foi detectado)

### 2.1 Tracker de work items
Azure DevOps · **Jira** · GitHub Issues · GitLab · nenhum.
→ Define qual MCP/CLI usar e como `create-work-item`/`start-workflow` criam e movem itens. Para Jira, use a skill `setup-jira`; para Azure, `setup-azure-mcp`. Atualize a tabela de tool-calls na `ai-tools-matrix.md`.

### 2.2 Time tracking
**7pace** · **Clockify** · **Toggl Track** · **Harvest** · 7pace+Clockify · nenhum.
→ O kit traz `scripts/sync-7pace.sh` (7pace, baseado em work item do Azure) e `.claude/integrations/timetracking/` (wrapper + Clockify). Para outras ferramentas, gere o script análogo a partir do modelo (ver "Adaptando o time tracking" abaixo) e ajuste `processes/timesync.md` + matrix. Se "nenhum", remova `timesync`/`setup-7pace` dos wrappers e a referência nos fluxos.

### 2.3 Qualidade de código
**SonarQube** (via MCP) · nenhum · outro.
→ Mantém/remove o passo 8 do `phase-code-review` e a skill `setup-sonarqube-mcp`. Ajuste `projectKey` (`<PROJECT_KEY>`).

### 2.4 Destino da documentação
**Repositório** (in-repo, default) · **Confluence** · **Outline** · **Notion** · outro.
→ Ver [`docs-target.md`](docs-target.md). Se externo, os fluxos publicam discovery/design/diário/post-mortem na plataforma e referenciam a URL no work item/PR (PRs ficam limpos). Configure o MCP/credenciais correspondentes.

### 2.5 Stack, adaptadores e comandos
Confirme os comandos reais: `<TEST_CMD>`, `<LINT_CMD>`, `<TYPECHECK_CMD>`, `<BUILD_CMD>`, `<E2E_CMD>`, e os caminhos `<src>`, `<e2e-dir>`. Se houver adaptadores compatíveis em `adapters/` (ex.: `adapters/stacks/angular/`), confirme quais acoplar para compor `.claude/PROJECT_REFERENCE.md`, fornecer checks específicos ao `phase-code-review` e sugerir comandos/presets de editor opcionais. Sem adaptador pronto para a stack, adapte os checks do `phase-code-review §2` diretamente aos padrões detectados.

### 2.6 Ferramentas de IA em uso
Claude Code · Antigravity · Gemini CLI · Codex · Cursor · Copilot · outras.
→ Mantenha apenas os wrappers das ferramentas usadas (os demais podem ficar como referência). Garanta que cada um aponte para `processes/*.md`. **Atenção:** `.agents/skills/` é compartilhado por Antigravity, Gemini CLI e Codex, e `GEMINI.md` depende de `AGENTS.md` — em projetos Gemini-only ou Antigravity-only, **preserve `AGENTS.md` e `.agents/skills/`** ao remover wrappers de outras ferramentas.

### 2.7 Pack de domínio (opcional)
Além dos adaptadores reutilizáveis em `adapters/`, pergunte se o usuário quer **gerar um domain pack** específico do negócio/domínio do projeto (skills de domínio: API, componentes, testes, convenções) a partir do `templates/project-reference.template.md` preenchido.

## Passo 3 — Apresentar o PLANO de adaptação

Mostre, e peça aprovação explícita:

1. **Mapa de placeholders → valores** (tabela): `<AZURE_ORG>`→…, `<PROJECT_KEY>`→…, `<TEST_CMD>`→…, etc.
2. **Adaptadores a acoplar:** lista de adaptadores selecionados (stack/cloud/observabilidade), usando os caminhos declarados em cada `adapter.json` (`files.conventions`, `files.review_checks` e, quando presentes, `files.editor_settings` e `files.skills`). Antes de propor qualquer gravação, compare os nomes (`name`) de todas as skills em `files.skills` **entre si** e com os processos já existentes em `processes/<name>.md`: se duas skills apontarem para o mesmo `processes/<name>.md` ou se esse destino já existir, destaque a colisão no plano e preserve os arquivos existentes até o usuário decidir como seguir (renomear, pular ou substituir).
3. **Arquivos a reescrever:** processos, wrappers (por ferramenta de IA), `ai-tools-matrix.md`, scripts.
4. **Skills a manter / remover / adicionar** (ex.: trocar `setup-azure-mcp`↔`setup-jira`; remover `timesync` se sem time tracking).
5. **MCPs a configurar** (`.mcp.json`): tracker, qualidade, docs, Figma, Playwright.
6. **Onde a documentação vai morar** (repo vs externo).

## Passo 4 — Aplicar (após aprovação)

1. Substituir placeholders em `processes/`, wrappers, `ai-tools-matrix.md`, scripts (use busca/substituição consistente; valide que nenhum `<PLACEHOLDER>` ficou para trás onde deveria ter valor). Ajustar também `.cursor/settings.json` conforme formatador, linter e extensões do projeto (mesclando o arquivo declarado em `files.editor_settings` de cada adaptador apenas quando presente e aprovado).
2. Acoplar os adaptadores selecionados usando os caminhos declarados no `adapter.json` de cada um: copiar apenas as pastas aprovadas para `adapters/` do projeto host (sem carregar adaptadores de outras stacks), compor o arquivo de `files.conventions` em `.claude/PROJECT_REFERENCE.md`, referenciar o arquivo de `files.review_checks` no `phase-code-review` e, quando o adaptador declarar `files.skills` (respeitando a resolução aprovada pelo usuário para eventuais colisões), copiar o conteúdo de cada `SKILL.md` como processo canônico em `processes/<name>.md` e gerar os wrappers finos correspondentes (`.agents/skills/<name>/SKILL.md`, `.claude/skills/<name>/SKILL.md`, `.cursor/rules/<name>.mdc`, `AGENTS.md` e `.github/copilot-instructions.md`) apontando para `processes/<name>.md` (ver Receita F de `GUIA-DE-EXPANSAO.md`).
3. Renomear/remover skills conforme o plano e ajustar todos os conjuntos de wrappers mantidos (`.agents/skills/`, `.claude/skills/`, `.cursor/rules/`, `AGENTS.md`, `GEMINI.md`, `.github/copilot-instructions.md`) + a `ai-tools-matrix.md` coerentemente — preservando `AGENTS.md` e `.agents/skills/` sempre que Antigravity, Gemini CLI ou Codex estiverem em uso.
4. Escrever/atualizar `.mcp.json` com os servidores escolhidos.
5. Configurar o time tracking escolhido (script + chaves no `.env.example`).
6. Configurar o destino de documentação (in-repo vs MCP externo).
7. Preencher `templates/project-reference.template.md` → `.claude/PROJECT_REFERENCE.md` com a arquitetura/convenções detectadas.
8. (Opcional) Gerar o domain pack para o stack.

## Passo 5 — Verificar e resumir

- `git status` / `git diff` — apresente um resumo do que mudou (rede de segurança).
- Liste os **próximos passos manuais**: preencher `.env` (a partir do `.env.example`), rodar `full-setup`/`setup-*`, autenticar MCPs.
- Aponte qualquer placeholder que **propositalmente** ficou para o usuário preencher.

---

## Adaptando o time tracking (modelos)

O contrato comum dos scripts: `--description`, `--start` (ISO 8601), `--end`, `--work-item-id` (quando aplicável), `--dry-run`. Para cada ferramenta, gere um `scripts/sync-<tool>.sh` que lê credenciais de variáveis de ambiente (NUNCA hardcode token) e faz o POST. Referência de API por ferramenta:

| Ferramenta | Auth | Endpoint de criação de entrada | Chaves no `.env` |
|---|---|---|---|
| **7pace** | `Authorization: Bearer` | `POST {base}/api/rest/workLogs?api-version=3.2` (vincula a work item) | `SEVENPACE_API_TOKEN`, `SEVENPACE_BASE_URL` |
| **Clockify** | `X-Api-Key` | `POST https://api.clockify.me/api/v1/workspaces/{wsId}/time-entries` | `CLOCKIFY_API_TOKEN`, `CLOCKIFY_WORKSPACE_ID`, `CLOCKIFY_PROJECT_ID` |
| **Toggl Track** | Basic (`{token}:api_token`) | `POST https://api.track.toggl.com/api/v9/workspaces/{wsId}/time_entries` | `TOGGL_API_TOKEN`, `TOGGL_WORKSPACE_ID`, `TOGGL_PROJECT_ID` |
| **Harvest** | `Authorization: Bearer` + `Harvest-Account-Id` | `POST https://api.harvestapp.com/v2/time_entries` | `HARVEST_API_TOKEN`, `HARVEST_ACCOUNT_ID`, `HARVEST_PROJECT_ID`, `HARVEST_TASK_ID` |

- O kit já inclui 7pace (`scripts/sync-7pace.sh`) e Clockify (`.claude/integrations/timetracking/`) como referência. Use-os como molde para Toggl/Harvest (mesma estrutura: parse de args → monta JSON → `curl` → trata HTTP code).
- Atualize `processes/timesync.md` com os exemplos da ferramenta escolhida e a `ai-tools-matrix.md` se houver tool-call de MCP associado.
- Conversão de fuso: lembre que o `sync-7pace.sh` envia `timeZone: -180` e trata a hora local com sufixo `Z` por convenção; o `sync-clockify.sh` converte `Z`→`-03:00`. Ajuste para o fuso/projeto correto.

## Referência de placeholders do kit

`<AZURE_ORG>` · `<AZURE_PROJECT>` · `<AREA_PATH>` · `<ORG>` · `<PROJECT_NAME>` · `<PROJECT_KEY>` · `<PROJECT_ROOT>` · `<APP_DIR>` · `<DAILY_WI>` · `<TEST_WI>` · `<SEVENPACE_ORG>` · `<7PACE_ACTIVITY_ID_*>` · `<CLOCKIFY_WORKSPACE_ID>` · `<CLOCKIFY_PROJECT_ID>` · `<CLOCKIFY_PROJECT_NAME>` · `<SONARQUBE_URL>` · `<TEST_CMD>` · `<LINT_CMD>` · `<TYPECHECK_CMD>` · `<BUILD_CMD>` · `<E2E_CMD>` · `<DEV_CMD>` · `<DEV_URL>` · `<src>` · `<e2e-dir>`.

Alguns exemplos usam também marcadores locais, explicados no próprio texto (ex.: `<SEU_SITE>`, `<US_ID>`, `<nome>`, `<SPACE>`, `<COLLECTION>` e `<PAGE>` em `docs-target.md`, `<OTHER_PROJECT>` em `templates/project-reference.template.md`).
