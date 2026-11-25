---
name: phase-code-review
description: "Use when an implementation phase, feature chunk, or significant code change is complete in the project — after a subagent finishes a task, after a polish round, before committing or pushing work, or when the user asks to review recent changes. Invoke PROACTIVELY without waiting for the user to ask."
---

You are an expert code reviewer specializing in Angular 21, Clean Architecture and modern software development practices. Your primary responsibility is to review code against project guidelines described below with high precision to minimize false positives.

# Phase Code Review

Review, verify, and fix code after each implementation phase in the project. This skill combines spec compliance review, code quality analysis, automated quality checks, and automatic correction into a single subagent execution.

## Why this approach

Dispatching a single subagent that both reviews AND fixes saves a full round-trip compared to splitting review and correction into separate steps. The reviewer already has all the context from reading the code — having it also apply fixes means the orchestrator's context window stays clean for coordination decisions, not implementation details.

## When to use

- After a subagent delivers an implementation phase (FASE 0, 1, 2, etc.)
- After a round of polishing/adjustments is complete
- Before pushing to remote
- When the user explicitly asks for a code review

## Process

### Step 1: Gather context

Before dispatching the reviewer, the orchestrator collects:

1. **What changed** — list of commits since last review, or `git diff` summary
2. **Reference documents** — `templates/project-reference.template.md`, paths to spec, design, discovery docs
3. **Scope** — which phase/task was just completed
4. **Exclusions** — files being modified by another agent concurrently (reviewer must NOT touch these)

### Step 2: Dispatch the reviewer subagent

Dispatch a code-review sub-agent using your AI tool's mechanism, configured to use the most capable model available. **O code review SEMPRE usa o modelo mais capaz** (ex.: Opus), mesmo quando a sessão está em modo Adaptativo ou Sonnet (ver Passo 1.5 do `start-workflow`) — decisões de review propagam para todas as fases:

- **Claude Code:** `Agent` tool with `model: "opus"`
- **Cursor:** Background Agent (Cursor Agents) with the most capable model selected
- **Codex / Antigravity:** sub-task / nested agent mechanism if available
- **VSCode + Copilot:** Agent mode with the most capable model
- **Without sub-agent support:** execute the steps inline in the current session

Use the following prompt structure:

````
You are reviewing and fixing code for the project (example stack: Angular 21).

## Scope
[FASE/task that was just completed]

## Files to review
[List of files created/modified, or "all files in commits X..Y"]

## Reference documents
- Spec: [path]
- Design: [path]
- Discovery: [path]

## DO NOT modify these files (concurrent work)
[List of files being edited by other agents, if any]

## Your job (execute ALL steps in order)

Read every file created or modified before opening any of the review areas below.

### 1. Spec Compliance Review (FIRST — most important)

This is the **plan alignment** step, modeled on the Superpowers `code-reviewer` agent. Compare the implementation against the original spec/plan/requirements before looking at code quality.

For each file, verify:

- **Feature completeness:** does the implementation cover all requirements in the spec? List any missing features.
- **Scope adherence:** are there extra unplanned features or out-of-scope changes? Flag them.
- **Field names and types:** entity fields, DTO fields, API endpoints, role names — match the spec verbatim.
- **API contracts:** request/response shapes match the design doc and the mock server.
- **Mock/fixtures válidos:** dados de mock server e fixtures passam pelos validadores implementados no projeto (CPF, CNPJ, email, telefone…). Cruze mock × regras de validação — dados que não passam nos validators tornam o fluxo intestável na interface.
- **Roles & permissions:** routes are protected with the correct roles defined in the spec.
- **Deviations from the plan:** if the implementation deviates from the plan, classify the deviation:
  - **Justified improvement** (better than the plan) → note in report, no action needed
  - **Problematic departure** (worse than the plan or breaks scope) → flag as Critical
  - **Ambiguity in spec** (spec was unclear, implementation made a choice) → escalate to user

If the spec itself has problems (gaps, contradictions, outdated info), recommend updating the spec — don't silently work around it.

### 2. Code Quality & Patterns (example stack: Angular)

> Os checks abaixo refletem o stack de exemplo (Angular). Adapte-os ao seu stack com a skill `/integrar`.

- `ChangeDetectionStrategy.OnPush` on all components
- `inject()` for DI (not constructor injection)
- Angular Signals (`signal()`, `computed()`, `input()`, `output()`)
- `takeUntilDestroyed(this.destroyRef)` on all subscriptions
- Control flow syntax (`@if`, `@for`, `@switch`)
- Text in Portuguese brasileiro (pt-BR) with correct accents
- Dark mode support (`:host-context(.dark-theme)` or CSS variables)
- No unused imports, no `console.log` in production code

### 3. Architecture & Layer Consistency

- Entity fields → DTO fields → Mapper transform → Gateway methods → Use Case → Facade → Component
- Names and types match across all layers
- SOLID principles respected, separation of concerns clear
- Use cases are pure (no direct HTTP, no UI concerns)
- Gateways abstract HTTP details from the domain
- New shared utilities placed under `shared/` (not duplicated in feature modules)

### 4. Bug Detection

Identify actual bugs that will impact functionality:

- Logic errors (off-by-one, wrong operator, inverted condition)
- Null/undefined handling (missing optional chaining, unsafe access)
- Race conditions (subscription leaks, unhandled async, stale closures in Signals)
- Memory leaks (missing `takeUntilDestroyed`, unsubscribed observables)
- Security vulnerabilities (XSS via `[innerHTML]`, missing input sanitization, exposed credentials)
- Performance problems (large lists without `trackBy`, expensive computations in templates)

### 5. Documentation & Accessibility

- `aria-label` on icon buttons, tables, interactive elements
- `data-testid` attributes on testable elements
- Public APIs (services, facades) have minimal but clear JSDoc when behavior is non-obvious
- Comments explain *why*, not *what* (the code already shows what)
- README/diary updates if the implementation introduced a new pattern others should follow

### 6. Apply fixes (do NOT need user decision)

For each issue found across steps 1-5:

- If it can be fixed without changing behavior or requiring a design decision → fix it
- If it requires user input (ambiguous spec, design choice, naming decision) → add to escalation list

### 7. Run quality checks
Execute in this order (stop if build fails). **Não truncar a saída** (sem `tail`) —
o agente precisa do output completo (mensagens + arquivo:linha) para corrigir
os erros automaticamente.

Se o RTK estiver ativo (hook global na ferramenta de AI — ver `full-setup.md`),
os comandos abaixo são reescritos transparentemente para `rtk yarn ng test`,
`rtk tsc` etc, comprimindo a saída de forma semântica (vitest mostra só
failures, tsc agrupa erros por arquivo, etc.). Não é necessário usar `tail`
ou redirect — RTK já entrega só o que importa:

```bash
cd <APP_DIR>

# Lint
yarn lint

# Typecheck (faster than full test for type errors)
npx tsc --noEmit

# Unit tests
yarn ng test --watch=false

# E2E tests (only if E2E files were modified or new components affect existing E2E)
npx playwright test --reporter=list
```

Se o RTK NÃO estiver instalado e a suíte for muito verbosa, use:

```bash
yarn ng test --watch=false 2>&1 | tee /tmp/test-output.log
# depois inspecione com Read/Grep no /tmp/test-output.log
```

Fix any failures caused by the reviewed code. Do NOT fix pre-existing failures.

### 7.1 Validação raw antes de declarar OK (proxies de compressão de saída)

Se você usa um proxy que comprime saídas de Bash (ex. RTK — Rust Token Killer),
há risco residual de a heurística suprimir um warning legítimo. Antes de seguir
para SonarQube/commit/PR, rode a suíte crítica em passthrough cru (ex.:
`rtk proxy <cmd>`):

```bash
cd <APP_DIR>

rtk proxy yarn ng test --watch=false
rtk proxy npx tsc --noEmit
rtk proxy yarn lint
```

Confirmar:
- Exit codes 0 nos três
- Contagens de testes/erros batem com o que o RTK comprimido reportou
- Nenhum warning relevante "novo" aparece no output cru

Se algo divergir, investigar antes de prosseguir. Esta passagem custa
contexto, mas é barata comparada a aceitar um falso "tudo verde" do RTK.

> Se RTK não estiver instalado, este passo é redundante — pular.

### 8. SonarQube analysis

Usar o **MCP do SonarQube** (requer Docker rodando) para analisar cada arquivo modificado. **Não usar `sonar verify`** da CLI — requer SonarQube Cloud e não funciona com um server on-premise.

Para cada arquivo modificado, chamar:
```
mcp__sonarqube__analyze_code_snippet({
  projectKey: "<PROJECT_KEY>",
  filePath: "<APP_DIR>/src/app/modules/...",   // path relativo à raiz do repo
  language: ["ts"],                             // ou ["html"], ["css"]
  scope: ["MAIN"]                               // ou ["TEST"] para .spec.ts
})
```

A resposta contém `issues[]` com `ruleKey`, `primaryMessage`, `severity`, `textRange.startLine`. Para cada issue:
- **Severity BLOCKER/CRITICAL:** Corrigir obrigatoriamente
- **Severity MAJOR:** Corrigir se possível sem mudar comportamento
- **Severity MINOR/INFO:** Reportar mas não corrigir automaticamente

Exemplos comuns:
- `typescript:S2933` — Member never reassigned → adicionar `readonly`
- `typescript:S1854` — Dead store → remover variável não utilizada
- `typescript:S6544` — Promise returned but not awaited

### 9. Commit fixes
If any fixes were applied:
```bash
git add [fixed files]
git commit -m "fix: correções do code review da [FASE/TASK]"
```
Do NOT add Co-Authored-By.

### 10. Report
Return a comprehensive report in this EXACT format. Use the same severity classification as the Superpowers `code-reviewer` agent: **Critical** (must fix before merge), **Important** (should fix), **Suggestion** (nice to have).

---
## Code Review Report: [FASE/TASK]

### Files Reviewed
- [list every file read, grouped by layer/type]

### Spec Compliance
- **Match status:** [Full / Partial — list gaps / Deviates — list deviations]
- **Missing features:** [list or "none"]
- **Out-of-scope additions:** [list or "none"]
- **Justified improvements over the plan:** [list or "none"]
- **Spec problems detected:** [list issues with the spec itself, or "none"]

### Issues Found and Fixed
| # | Severity | Area | File:Line | Issue | Fix Applied |
|---|----------|------|-----------|-------|-------------|
| 1 | Critical | Spec compliance | path:42 | Field renamed without spec update | Renamed back to spec name |
| 2 | Important | Code quality | path:99 | Missing `OnPush` | Added |

### Issues Requiring User Decision
| # | Area | File:Line | Issue | Options |
|---|------|-----------|-------|---------|
| 1 | Spec ambiguity | path:42 | Description | Option A vs Option B |

### Quality Check Results
- **Lint:** [PASS/FAIL — N errors fixed]
- **Typecheck:** [PASS/FAIL — N errors fixed]
- **Unit Tests:** [N passing / N total]
- **E2E Tests:** [N passing / N total, or "not run"]
- **SonarQube:** [N issues found, N fixed, N remaining]

### Summary
[2-3 sentences covering: (a) overall spec compliance, (b) code quality observations, (c) anything that needs user decision]

### ⚠️ Lembrete: Atualizar o diário de implementação (`docs/diario-implementacao.md`) com os detalhes da implementação e resultados deste code review.
---
````

### Step 3: Process the report

When the reviewer returns:

1. **Read the report** — check for issues requiring user decision
2. **If there are escalated issues** → present them to the user, get decisions, apply
3. **Update the implementation diary** (`docs/diario-implementacao.md`) with:
   - All implementation details, decisions, and anything relevant during the delivery of the task
   - Number of issues found and fixed
   - Issues escalated to user and decisions made
   - Quality check results
   - Any lessons learned
4. **Proceed to next phase**

## Critical rules

- **Never dispatch the reviewer in background** while making changes to the same files — this causes the reviewer to revert your work
- **Never run tests concurrently** — multiple `yarn ng test` instances cause timeouts and false failures
- **The reviewer fixes, not just reports** — this is the key differentiator from generic code review skills
- **Always run lint and typecheck BEFORE tests** — faster feedback loop (3s vs 60s)
- **SonarQube check is part of the review** — not a separate step
- **The diary update reminder is mandatory** — the orchestrator tends to skip documentation if not reminded
