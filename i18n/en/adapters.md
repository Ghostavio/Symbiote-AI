# Symbiote-AI Adapters (`adapters/`)

> English companion to [`adapters/README.md`](../../adapters/README.md) *(canonical pt-BR)*. See also [`README.en.md`](../../README.en.md) and [`i18n/README.md`](../README.md).

The **Symbiote-AI** core (`processes/`, `AGENTS.md`, `GEMINI.md`, wrappers, and `.cursor/settings.json`) is **stack-neutral**. Specializations by technology, cloud provider, or observability live under `adapters/` as **optional, composable adapters**, selectively coupled via `simbiose` (and its integration procedure in [`processes/integrar.md`](../../processes/integrar.md)).

A single project can combine orthogonal adapters (for example: `stacks/angular` + `cloud/aws` + `observability/opentelemetry`, or `stacks/react` + `cloud/cloudflare` + `observability/opentelemetry`).

## Category structure

```text
adapters/
├── stacks/          # Frameworks and languages (e.g. angular, react, ...)
├── cloud/           # Cloud providers and infrastructure (e.g. cloudflare, aws, ...)
└── observability/   # Telemetry, logs, metrics, tracing, and SLOs
```

## Available adapters

| Category | ID | What it provides |
| --- | --- | --- |
| `stack` | [`angular`](../../adapters/stacks/angular/conventions.md) | Modern Angular conventions (standalone, Signals, `OnPush`, `inject()`, Vitest, Playwright), checks for `phase-code-review`, and editor preset |
| `stack` | [`react`](../../adapters/stacks/react/conventions.md) | Modern React conventions (functional components, Hooks, client/server state, RSC, component/E2E testing, and TypeScript when configured), checks for `phase-code-review`, and editor preset |
| `cloud` | [`cloudflare`](../../adapters/cloud/cloudflare/conventions.md) | Cloudflare Workers/Pages conventions (official MCP connectors + Wrangler CLI, bindings, secrets, KV/D1/R2/Durable Objects/Queues, edge caching, isolated runtime) and checks for `phase-code-review` |
| `cloud` | [`aws`](../../adapters/cloud/aws/conventions.md) | AWS and IaC conventions (official AWS MCP + AWS CLI/IaC, least-privilege IAM, secrets, Lambda/ECS, SQS/SNS/EventBridge, S3/DynamoDB/RDS, resilience, cost) and checks for `phase-code-review` |
| `observability` | [`opentelemetry`](../../adapters/observability/opentelemetry/conventions.md) | Vendor-neutral OpenTelemetry conventions (correlated structured logs, W3C tracing, bounded-cardinality RED/USE metrics, PII redaction, SLOs, and safe Kubernetes `kubectl` log inspection) and checks for `phase-code-review` |

> New adapters (other stacks, clouds, or observability tools) follow the contract below and Recipe G in [`expansion-guide.md`](expansion-guide.md).

## Adapter contract

Each adapter lives under `adapters/<category_dir>/<id>/` (where `<category_dir>` is `stacks`, `cloud`, or `observability`) and must provide a valid `adapter.json` manifest automatically verified by [`scripts/validate-kit.py`](../../scripts/validate-kit.py):

```json
{
  "id": "angular",
  "name": "Angular",
  "category": "stack",
  "version": "1.0.0",
  "description": "Short summary of the adapter scope.",
  "detect": {
    "files": ["angular.json"],
    "packages": ["@angular/core", "@angular/cli"]
  },
  "commands": {
    "lint": "yarn lint",
    "typecheck": "npx tsc --noEmit",
    "test": "yarn ng test --watch=false",
    "e2e": "npx playwright test --reporter=list"
  },
  "files": {
    "conventions": "conventions.md",
    "review_checks": "review-checks.md",
    "editor_settings": "editor-settings.json"
  }
}
```

### `adapter.json` fields

- **`id`** *(required)*: kebab-case identifier (`^[a-z0-9][a-z0-9-]*$`), matching the directory name.
- **`name`** *(required)*: human-readable adapter name.
- **`category`** *(required)*: `"stack"` (under `adapters/stacks/`), `"cloud"` (under `adapters/cloud/`), or `"observability"` (under `adapters/observability/`).
- **`version`** *(optional)*: semantic version of the adapter (e.g. `"1.0.0"`).
- **`description`** *(required)*: concise summary of when to apply the adapter.
- **`detect`** *(required)*: object with at least one non-empty list among `files`, `packages`, or `directories` — used by `simbiose`/`integrar` to suggest coupling automatically (avoid generic filenames that cause cross-stack false positives).
- **`commands`** *(optional)*: suggested commands to populate `<LINT_CMD>`, `<TYPECHECK_CMD>`, `<TEST_CMD>`, `<E2E_CMD>`, `<BUILD_CMD>`, or `<DEV_CMD>` when not detected directly in the project (omit tools that are not guaranteed to be installed in the host).
- **`files`** *(required)*: relative paths contained inside the adapter directory (filenames may be customized as long as they match the manifest and stay within the adapter directory):
  - `conventions` *(required)*: code, architecture, and testing conventions composed into `.claude/PROJECT_REFERENCE.md` and `AGENTS.md`.
  - `review_checks` *(required)*: specialized checklist loaded by [`processes/phase-code-review.md`](../../processes/phase-code-review.md) (§2–§4) from the path declared in `adapter.json`.
  - `editor_settings` *(optional)*: JSON with language-scoped editor/formatter preferences (at the path declared in `files.editor_settings`) merged into `.cursor/settings.json` upon approval.
  - `skills` *(optional)*: list of relative subdirectories containing a `SKILL.md` with valid frontmatter (`name` and `description`). When coupled, each approved skill is installed following the kit's single-source-of-truth convention: its body becomes a canonical procedure in `processes/<name>.md`, and thin wrappers (`.agents/skills/<name>/SKILL.md`, `.claude/skills/<name>/SKILL.md`, `.cursor/rules/<name>.mdc`, `AGENTS.md`, `.github/copilot-instructions.md`) point to it.

## How coupling works

1. **Detection (`simbiose` / `integrar`):** inspects the host project using the `detect` signals in available `adapters/*/*/adapter.json` manifests (or the user's explicit selection for new projects).
2. **Plan with confirmation and collision checks:** presents which adapters will be coupled, the paths declared in each `adapter.json` (`files.conventions`, `files.review_checks`, `files.editor_settings`, and `files.skills`), and checks for skill name collisions across selected adapters or against existing `processes/<name>.md`. On collision, the conflict is surfaced in the plan and existing files are preserved until the user decides.
3. **Selective installation:** copies only approved adapters into the host project's `adapters/` directory (never carrying unrelated stacks), composes `files.conventions` into `.claude/PROJECT_REFERENCE.md`, references `files.review_checks` in the review flow, merges `files.editor_settings` only when present and approved, and installs approved `files.skills` as canonicals in `processes/<name>.md` plus thin wrappers for active AI tools (if the user skips a colliding skill while keeping both adapters in `adapters/`, both adapters remain valid and only the chosen skill enters `processes/`).
