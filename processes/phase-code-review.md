---
name: phase-code-review
description: "Use para revisar código quando solicitado ou após uma entrega que justifique revisão. Ajuste a profundidade ao risco e aplique correções somente dentro do escopo autorizado."
---

# Phase Code Review

Compare a mudança com a intenção e as convenções do projeto. Use a profundidade necessária para identificar regressões e verificar o resultado.

## Escolher o escopo da revisão

- **Avaliação:** quando o usuário pede uma revisão, auditoria ou parecer, inspecione o diff, rode verificações relevantes e reporte achados. Preserve os arquivos, commits e registros externos.
- **Revisão de implementação:** quando o pedido já autoriza implementar ou corrigir, aplique correções focadas dentro desse escopo. Reporte decisões de produto ou mudanças de comportamento fora do escopo para avaliação.
- **Profundidade:** revise mudanças pequenas, reversíveis e verificáveis na própria sessão. Para mudanças de alto impacto ou complexidade, busque revisão independente se disponível e autorizada. Siga a [estratégia de esforço e modelo](start-workflow.md#passo-15--esforço-e-seleção-de-modelo) e sugira ajustes conforme o risco da revisão. Se a revisão independente não estiver disponível, faça as verificações possíveis e sinalize a limitação.

## Process

### Step 1: Gather context

Antes de iniciar a revisão, reúna:

1. **What changed** — list of commits since last review, or `git diff` summary
2. **Reference documents** — `.claude/PROJECT_REFERENCE.md` (ou `templates/project-reference.template.md`), paths to spec, design, discovery docs, and `review-checks.md` of any active adapters under `adapters/`
3. **Scope** — which phase/task was just completed
4. **Exclusions** — files being modified by another agent concurrently (reviewer must NOT touch these)

### Step 2: Executar a revisão

Use o roteiro abaixo na sessão atual ou compartilhe-o com um reviewer autorizado. Se usar um reviewer, informe os arquivos protegidos, o modo de revisão e a autorização disponível para editar ou executar verificações.

Use the following prompt structure:

````
Review the proposed change using the stack and conventions documented in `.claude/PROJECT_REFERENCE.md` and `docs/discovery.md` when available.

## Review mode
[Assessment or implementation review, including any explicitly authorized edits]

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

## Review checklist

Read the diff and open the relevant surrounding code. Select the checks that apply to the change; use the project’s own conventions.

### 1. Spec Compliance Review

This is the **plan alignment** step, modeled on the Superpowers `code-reviewer` agent. Compare the implementation against the original spec, plan or requirements when available. For a small change, use the stated intent and acceptance criteria.

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

> Verifique contra os padrões da stack configurada no projeto (`.claude/PROJECT_REFERENCE.md` e `docs/discovery.md`). Quando houver adaptadores acoplados em `adapters/` (ex.: `adapters/stacks/angular/review-checks.md`), aplique também os checks específicos de cada adaptador ativo.

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

### 6. Tratar achados conforme a autorização

Na avaliação, reporte os achados e suas consequências. Na revisão de implementação, aplique as correções já autorizadas e encaminhe decisões fora do escopo ao responsável pela mudança.

### 7. Run quality checks
Identifique os comandos na documentação, configuração ou CI do projeto. Rode lint, checagem de tipos e testes conforme a stack e o risco da mudança. Comece pelas verificações mais rápidas quando isso ajudar a obter feedback. Se um check aplicável estiver indisponível, registre a limitação e rode os demais.

Preserve a saída completa (mensagens e arquivo:linha) para diagnosticar falhas. Use os comandos reais do projeto (substitua os marcadores pelos comandos detectados ou configurados via `/simbiose`):

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
<TEST_CMD> > /tmp/test-output.log 2>&1
TEST_STATUS=$?
# inspecione /tmp/test-output.log com Read/Grep e confira TEST_STATUS (0 = sucesso)
```

Identifique quais falhas foram causadas pela mudança. Na revisão de implementação, corrija as falhas introduzidas que estiverem no escopo. Registre falhas preexistentes separadamente quando forem relevantes.

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
- **Severity BLOCKER/CRITICAL:** Reportar como bloqueio. Aplicar correção quando autorizada.
- **Severity MAJOR:** Reportar impacto e corrigir se estiver no escopo autorizado.
- **Severity MINOR/INFO:** Reportar mas não corrigir automaticamente

Exemplos comuns:
- `typescript:S2933` — Member never reassigned → adicionar `readonly`
- `typescript:S1854` — Dead store → remover variável não utilizada
- `typescript:S6544` — Promise returned but not awaited

### 9. Registrar correções

Se a entrega já inclui commit, siga as convenções do projeto e inclua apenas as correções autorizadas. Na avaliação, entregue os achados sem alterar a branch.

### 10. Reportar

Apresente primeiro os achados por severidade, com arquivo e linha, impacto e verificação. Indique o que foi corrigido, o que ficou pendente e quais verificações foram executadas ou indisponíveis. Use o modelo abaixo quando o volume de trabalho justificar esse detalhamento.

## Code Review Report: [FASE/TASK]

### Files Reviewed
- [list every file read, grouped by layer/type]

### Spec Compliance
- **Match status:** [Full / Partial — list gaps / Deviates — list deviations]
- **Missing features:** [list or "none"]
- **Out-of-scope additions:** [list or "none"]
- **Justified improvements over the plan:** [list or "none"]
- **Spec problems detected:** [list issues with the spec itself, or "none"]

### Findings and fixes
| # | Severity | Area | File:Line | Issue | Status |
|---|----------|------|-----------|-------|-------------|
| 1 | Critical | Spec compliance | path:42 | Field renamed without spec update | Renamed back to spec name |
| 2 | Important | Code quality | path:99 | Uncleaned resource handle / missing error check | Fixed |

### Issues Requiring User Decision
| # | Area | File:Line | Issue | Options |
|---|------|-----------|-------|---------|
| 1 | Spec ambiguity | path:42 | Description | Option A vs Option B |

### Quality Check Results
- **Lint:** [resultado e limitações]
- **Typecheck:** [resultado e limitações]
- **Unit Tests:** [N passing / N total]
- **E2E Tests:** [N passing / N total, or "not run"]
- **Análise estática:** [ferramenta, resultado e limitações; inclua SonarQube quando usado]

### Summary
[2-3 sentences covering: (a) overall spec compliance, (b) code quality observations, (c) anything that needs user decision]

---
````

### Step 3: Encerrar

Entregue o relatório ou use os achados para continuar a implementação autorizada. Em uma entrega que já usa diário ou tracker, registre a evidência no local adotado pelo projeto quando isso fizer parte da entrega.

## Critical rules

- **Isole a revisão paralela** de arquivos que estão sendo editados para evitar alterações concorrentes.
- **Isole verificações concorrentes** quando compartilharem arquivos, portas ou outros recursos de execução.
- **Priorize verificações rápidas quando disponíveis** para antecipar falhas antes das suítes mais longas.
- **Análise estática faz parte da revisão.** Use as verificações locais e registre se houve análise complementar no SonarQube.
