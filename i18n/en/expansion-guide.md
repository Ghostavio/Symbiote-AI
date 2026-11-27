# Expansion Guide — Swapping and Adding Tools

> English companion to [`GUIA-DE-EXPANSAO.md`](../../GUIA-DE-EXPANSAO.md) *(canonical pt-BR)*. See also [`README.en.md`](../../README.en.md) and [`i18n/README.md`](../README.md).

How to adapt the kit to other tools: **Jira instead of Azure DevOps**, **Toggl/Harvest instead of 7pace**, **Confluence/Outline instead of in-repo docs**, and how to **add a new AI tool**, **skill**, **adapter**, or **language**.

> **Shortcut:** the **`simbiose`** skill automates most of this guide (detects project context and compatible adapters, proposes a plan, and adapts files after your confirmation). Use this guide to understand what it does — or for manual tweaks.

## Mental model

Everything revolves around 4 pieces:

1. **Canonical procedures** (`processes/*.md`) — tool-neutral logic in `pt-BR`. **Rarely change.**
2. **Per-AI-tool wrappers** (`.agents/skills/`, `.claude/skills/`, `.cursor/rules/`, `AGENTS.md`, `GEMINI.md`, `.github/copilot-instructions.md`) — thin pointers.
3. **`ai-tools-matrix.md`** — MCP tool-call mapping across AI tools.
4. **Placeholders** (`<AZURE_ORG>`, `<PROJECT_KEY>`, `<TEST_CMD>`, `<src>`, …) — project-specific values.

Expanding = editing (2), (3), and placeholders — almost never touching (1).

---

## Recipe A — Azure DevOps → Jira

1. **MCP:** run `/setup-jira` (or follow [`processes/setup-jira.md`](../../processes/setup-jira.md)). Option A = official Atlassian MCP (OAuth, covers both Jira **and** Confluence); Option B = `mcp-atlassian` with API token (Cloud or Server/DC).
2. **Skills:** keep `setup-jira` and remove/ignore `setup-azure-mcp` in wrappers (or keep both as reference).
3. **Tool-calls:** in `ai-tools-matrix.md` (*Jira / Atlassian MCP* section), procedures map to:
   - create item → `createJiraIssue` (instead of `wit_create_work_item`)
   - query → **JQL** `searchJiraIssuesUsingJql` (instead of WIQL)
   - **move column → workflow transition** `transitionJiraIssue` (Jira uses workflow transitions rather than free-form columns)
4. **Workflows:** map the review stage to your team's actual Jira transition, following [the integration procedure](../../processes/integrar.md#21-tracker-de-work-items). Use the issue types and hierarchy configured by the team (e.g. Epic → Story → Sub-task).
5. **Env:** `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN` (Option B) — always from environment variables.

> The same official Atlassian MCP also enables publishing docs to **Confluence** (see Recipe C).

---

## Recipe B — 7pace → Toggl / Clockify / Harvest

All time-tracking scripts share a common CLI contract (`--description --start --end [--work-item-id] [--dry-run]`). Create a `scripts/sync-<tool>.sh` modeled after `scripts/sync-7pace.sh`, reading credentials from env vars:

| Tool | Auth | Endpoint | Env |
|---|---|---|---|
| Toggl Track | Basic `{token}:api_token` | `POST https://api.track.toggl.com/api/v9/workspaces/{wsId}/time_entries` | `TOGGL_API_TOKEN`, `TOGGL_WORKSPACE_ID`, `TOGGL_PROJECT_ID` |
| Clockify | `X-Api-Key` | `POST https://api.clockify.me/api/v1/workspaces/{wsId}/time-entries` | `CLOCKIFY_API_TOKEN`, `CLOCKIFY_WORKSPACE_ID`, `CLOCKIFY_PROJECT_ID` |
| Harvest | `Bearer` + `Harvest-Account-Id` | `POST https://api.harvestapp.com/v2/time_entries` | `HARVEST_API_TOKEN`, `HARVEST_ACCOUNT_ID`, `HARVEST_PROJECT_ID`, `HARVEST_TASK_ID` |

Steps: copy `sync-7pace.sh`/`sync-clockify.sh` as a template → adjust auth/endpoint/payload → update `processes/timesync.md` with examples for the new tool → if an MCP exists, add it to the matrix. (Clockify is already bundled under `.claude/integrations/timetracking/`.)

> **Candidate adapter (Jira):** [Tempo Timesheets for Jira](https://marketplace.atlassian.com/apps/6572/timesheets-by-tempo-jira-time-tracking?hosting=cloud&tab=overview) is listed as a candidate for Jira teams until a verified integration is delivered.

---

## Recipe C — In-repo docs → external platform (clean PRs)

Follow [`processes/docs-target.md`](../../processes/docs-target.md):

1. Set `DOC_TARGET=confluence|outline|notion`.
2. **Confluence:** use the official Atlassian MCP (`createConfluencePage`/`updateConfluencePage`) in space `CONFLUENCE_SPACE_KEY`. **Outline:** REST API (`documents.create`). **Notion:** Notion MCP/API.
3. Workflows now **publish** discovery/design/journal/post-mortem pages to the platform and link the **URL** in the work item and PR — no process `.md` files are committed.

---

## Recipe D — SonarQube → another tool / none

- **None:** remove step 8 (SonarQube) from [`processes/phase-code-review.md`](../../processes/phase-code-review.md) and drop `setup-sonarqube-mcp` from wrappers.
- **Another linter/quality tool:** replace the `mcp__sonarqube__analyze_code_snippet` call with the equivalent tool and update `<PROJECT_KEY>`.

---

## Recipe E — Add a new AI tool (e.g. Windsurf, Zed)

1. Identify the tool's discovery convention (file or directory it reads).
2. Create thin **wrappers** in that format pointing to `processes/<name>.md` (never duplicate procedure content).
3. Add a row to the *Supported tools* table in `ai-tools-matrix.md` and, if the tool uses a single entry point (like `AGENTS.md`), list the procedures there.
4. Map the tool's MCP tool-call names in the matrix sections.
5. Install **Superpowers** in the tool (the matrix documents the command per tool).

---

## Recipe F — Add a new skill/process

1. Create the canonical procedure `processes/<name>.md` (with `name`/`description` frontmatter).
2. Create wrappers: `.agents/skills/<name>/SKILL.md`, `.claude/skills/<name>/SKILL.md`, and `.cursor/rules/<name>.mdc` pointing directly to the canonical.
3. Add a row to the process tables in `AGENTS.md` **and** `.github/copilot-instructions.md`.
4. If the skill uses an MCP, document its tool-calls in `ai-tools-matrix.md`.

---

## Recipe G — Add a new adapter (stack, cloud, or observability)

To specialize the kit for a technology (e.g. React, Cloudflare, AWS, OpenTelemetry) without coupling the neutral core, follow the contract in [`adapters.md`](adapters.md) (canonical: [`adapters/README.md`](../../adapters/README.md)):

1. Create `adapters/<category_dir>/<id>/`, where `<category_dir>` is `stacks`, `cloud`, or `observability`.
2. Create `adapter.json` with `id`, `name`, `category`, `description`, `detect` signals (`files`, `packages`, or `directories`), optional `commands` (only when guaranteed on the host), and `files` (`conventions`, `review_checks`, and optional `editor_settings`/`skills`).
3. Write the files declared in `files.conventions` (for `.claude/PROJECT_REFERENCE.md`) and `files.review_checks` (for `phase-code-review`) — filenames may be customized as long as they are declared in `adapter.json` and stay inside the adapter directory.
4. Validate manifests and links with `python3 -B scripts/validate-kit.py` and `python3 -B -m unittest discover -s tests -v`.

---

## Recipe H — Add a new language (i18n)

Symbiote-AI is **Brazil-first** (`pt-BR` remains the single canonical language in `processes/`), while user-facing documentation supports additional languages under `i18n/` (see [`i18n/README.md`](../README.md)):

1. Create `README.<locale>.md` at the repository root matching the `## ` section structure of `README.md`, with a language switcher linking back to `README.md`.
2. Add the link to `README.<locale>.md` in the language switcher at the top of `README.md`.
3. Create `i18n/<locale>/` with translated companion guides matching the `## ` section structure of their canonical `pt-BR` sources.
4. Register the new locale and its `source` → `target` mappings in `i18n/i18n.json`.
5. Run `python3 -B scripts/validate-kit.py` and `python3 -B -m unittest discover -s tests -v` to check H2 (`## `) section counts, reciprocal README links, and internal links (semantic correspondence of sections and top-of-file switcher placement remain part of content review).

---

## Post-expansion checklist

- [ ] No `<PLACEHOLDER>` left where a real value is expected (`grep -rnE '<[A-Z0-9_]+>|<src>|<e2e-dir>' .`).
- [ ] `.env.example` updated with new keys; `.env` listed in `.gitignore`.
- [ ] All active AI tool wrappers point to `processes/`.
- [ ] `ai-tools-matrix.md` reflects the real MCPs in use.
- [ ] One end-to-end flow tested (e.g. `start-workflow` → Express → PR).
