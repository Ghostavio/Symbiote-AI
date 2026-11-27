---
name: phase-code-review
description: "Use when an implementation phase, feature chunk, or significant code change is complete in the project — after a subagent finishes a task, after a polish round, before committing or pushing work, or when the user asks to review recent changes. Invoke PROACTIVELY without waiting for the user to ask."
---

You are an expert code reviewer specializing in clean architecture, maintainable software design, and the idioms of the project's configured stack. Your primary responsibility is to review code against project guidelines described below with high precision to minimize false positives.

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
You are reviewing and fixing code for the project (follow the stack, architecture, and conventions documented in `.claude/PROJECT_REFERENCE.md` and `docs/discovery.md`).

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

### 2. Code Quality & Patterns

> Verifique contra os padrões da stack configurada no projeto (`.claude/PROJECT_REFERENCE.md` e `docs/discovery.md`).

- Idiomatic use of the project's language, framework, and state/reactivity patterns
- Proper dependency injection, error handling, and resource cleanup (connections, timers, listeners, subscriptions, file handles)
- Clear control flow and small, readable functions/components without unnecessary complexity
- User-facing copy in the project's configured language (default pt-BR with proper accents)
- Consistent styling/theming and design tokens when touching UI (including dark mode if supported)
- No unused imports, dead code, or debug logging left in production code

### 3. Architecture & Layer Consistency

- Respect the project's module and layer boundaries (e.g., domain → data/infra → application/use cases → presentation/API)
- Names, types, and contracts match across all layers
- SOLID principles respected, separation of concerns clear
- Core domain/business logic stays decoupled from transport/UI details
- Infrastructure/gateways abstract external I/O details from the domain
- New shared utilities placed in the project's shared module/package (not duplicated across features)

### 4. Bug Detection

Identify actual bugs that will impact functionality:

- Logic errors (off-by-one, wrong operator, inverted condition)
- Null/undefined/nil handling (missing guards, unsafe access)
- Race conditions (unhandled async, stale state, concurrent mutation hazards)
- Resource and memory leaks (unclosed handles/connections, uncleaned timers, listeners, or subscriptions)
- Security vulnerabilities (injection, XSS, missing input validation/sanitization, exposed credentials)
- Performance problems (N+1 queries, unbounded lists/renders, expensive computations in hot paths)

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
Identifique os comandos na documentação, configuração ou CI do projeto. Rode lint, checagem de tipos e testes conforme a stack e o risco da mudança. Comece pelas verificações mais rápidas quando isso ajudar a obter feedback. Se um check aplicável estiver indisponível, registre a limitação e rode os demais.

Preserve a saída completa (mensagens e arquivo:linha) para diagnosticar falhas. Use os comandos reais do projeto (substitua os marcadores abaixo via `/integrar`):

Se o RTK estiver ativo (hook global na ferramenta de AI — ver `full-setup.md`),
os comandos abaixo são reescritos transparentemente para `rtk <cmd>`,
comprimindo a saída de forma semântica (mostrando apenas falhas e erros
agrupados por arquivo). Não é necessário usar `tail` ou redirect — RTK já
entrega só o que importa:

```bash
# Lint / análise estática local
<LINT_CMD>

# Typecheck / build check (quando aplicável à stack)
<TYPECHECK_CMD>

# Unit tests
<TEST_CMD>

# E2E / integration tests (only if E2E files were modified or behavior affects existing E2E)
<E2E_CMD>
```

Se o RTK NÃO estiver instalado e a suíte for muito verbosa, use:

```bash
<TEST_CMD> 2>&1 | tee /tmp/test-output.log
# depois inspecione com Read/Grep no /tmp/test-output.log
```

Fix any failures caused by the reviewed code. Do NOT fix pre-existing failures.

### 7.1 Validação raw antes de declarar OK (proxies de compressão de saída)

Se você usa um proxy que comprime saídas de Bash (ex. RTK — Rust Token Killer),
há risco residual de a heurística suprimir um warning legítimo. Antes de seguir
para a análise complementar, o commit ou o PR, rode as verificações críticas do passo 7 em passthrough cru (ex.: `rtk proxy <cmd>`):

```bash
rtk proxy <TEST_CMD>
rtk proxy <TYPECHECK_CMD>
rtk proxy <LINT_CMD>
```

Confirmar:
- Códigos de saída das verificações executadas
- Contagens de testes/erros batem com o que o RTK comprimido reportou
- Nenhum warning relevante "novo" aparece no output cru

Se algo divergir, investigar antes de prosseguir. Esta passagem custa
contexto, mas é barata comparada a aceitar um falso "tudo verde" do RTK.

> Se RTK não estiver instalado, este passo é redundante — pular.

### 8. Análise estática local e SonarQube opcional

Priorize as ferramentas de análise estática já configuradas no projeto e aproveite os resultados do lint do passo 7.

- **JavaScript e TypeScript com ESLint:** recomende o [`eslint-plugin-sonarjs`](https://github.com/SonarSource/SonarJS/blob/master/packages/analysis/src/jsts/rules/README.md) para obter regras do SonarJS localmente, sem servidor. Quando já estiver configurado, use o comando de lint do projeto. Se estiver ausente, sugira a configuração compatível com a versão do ESLint, sem instalar dependências durante a revisão.
- **Outras stacks:** use o analisador local configurado no projeto. Se nenhum estiver disponível, registre essa limitação e prossiga com as demais verificações.
- **SonarQube:** use o MCP como complemento quando o projeto já tiver a integração e a análise centralizada for relevante. Se o MCP estiver indisponível, registre a limitação e prossiga com as verificações locais. As regras do plugin ESLint cobrem parte da análise JS/TS disponível no SonarQube.

Se usar o MCP, analise os arquivos modificados:
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
| 2 | Important | Code quality | path:99 | Uncleaned resource handle / missing error check | Fixed |

### Issues Requiring User Decision
| # | Area | File:Line | Issue | Options |
|---|------|-----------|-------|---------|
| 1 | Spec ambiguity | path:42 | Description | Option A vs Option B |

### Quality Check Results
- **Lint:** [PASS/FAIL — N errors fixed]
- **Typecheck:** [PASS/FAIL — N errors fixed]
- **Unit Tests:** [N passing / N total]
- **E2E Tests:** [N passing / N total, or "not run"]
- **Análise estática:** [ferramenta, resultado e limitações; inclua SonarQube quando usado]

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
- **Never run tests concurrently** — multiple test runner instances in the same workspace cause timeouts and false failures
- **The reviewer fixes, not just reports** — this is the key differentiator from generic code review skills
- **Priorize verificações rápidas quando disponíveis** para antecipar falhas antes das suítes mais longas.
- **Análise estática faz parte da revisão.** Use as verificações locais e registre se houve análise complementar no SonarQube.
- **The diary update reminder is mandatory** — the orchestrator tends to skip documentation if not reminded
