# Review Checks — Adaptador Angular

Checklist especializado para carregar em [`processes/phase-code-review.md`](../../../processes/phase-code-review.md) (§2, §3, §4 e §7) quando o adaptador `angular` estiver acoplado ao projeto.

## §2 Code Quality & Patterns (Angular)

- [ ] `ChangeDetectionStrategy.OnPush` declarado em todos os componentes novos ou alterados.
- [ ] `inject()` usado para injeção de dependências (sem regressão para constructor injection em código novo).
- [ ] Uso idiomático de Angular Signals (`signal()`, `computed()`, `input()`, `output()`) em vez de estado mutável solto ou sujeitos RxJS desnecessários.
- [ ] `takeUntilDestroyed(this.destroyRef)` (ou `toSignal()` / `async` pipe) em todas as subscriptions RxJS.
- [ ] Sintaxe moderna de control flow (`@if`, `@for` com `track` estável, `@switch`) em vez de diretivas estruturais legadas (`*ngIf`/`*ngFor`).
- [ ] Suporte consistente a dark mode (`:host-context(.dark-theme)` ou variáveis CSS) quando o projeto oferece temas.
- [ ] Sem imports não utilizados, código morto ou `console.log` em código de produção.

## §3 Architecture & Layer Consistency (Angular)

- [ ] Consistência de nomes e tipos entre camadas: `Entity → DTO → Mapper → Gateway → Use Case → Facade → Component`.
- [ ] Use cases permanecem puros (sem `HttpClient`, router ou detalhes de UI).
- [ ] Gateways abstraem completamente detalhes de HTTP/API do domínio.
- [ ] Rotas de feature carregadas com lazy loading (`loadChildren` / `loadComponent`) e protegidas pelos guards/roles previstos na spec.
- [ ] Utilitários e componentes reutilizáveis colocados em `shared/` (sem duplicação entre módulos).

## §4 Bug Detection (Angular)

- [ ] **Vazamento de memória:** subscriptions sem `takeUntilDestroyed` ou `unsubscribe`, listeners DOM não removidos.
- [ ] **Race conditions / reatividade:** closures obsoletas em `effect()`/`computed()`, requisições concorrentes sem cancelamento (`switchMap` quando apropriado) ou async sem tratamento de erro.
- [ ] **Segurança:** risco de XSS via `[innerHTML]` sem sanitização explícita (`DomSanitizer`), credenciais ou tokens expostos em logs/bundles.
- [ ] **Performance:** `@for` sem `track` adequado em listas grandes, chamadas pesadas diretamente no template executadas a cada ciclo de detecção de mudanças.

## §5 Accessibility & Tests (Angular)

- [ ] `aria-label` em botões de ícone, tabelas e controles interativos.
- [ ] Atributos `data-testid` em elementos críticos para E2E (sem dependência de classes CSS).
- [ ] Testes unitários compatíveis com o runner do projeto (em Vitest com `@angular/build:unit-test`: sem `fakeAsync`/`tick` e sem `TestBed.initTestEnvironment()`).

## §7–§8 Quality Checks & Static Analysis (exemplos Angular)

Comandos típicos (ajuste ao gerenciador de pacotes e scripts reais do projeto):

```bash
yarn lint                         # ESLint (recomendado com eslint-plugin-sonarjs)
npx tsc --noEmit                  # Typecheck
yarn ng test --watch=false        # Testes unitários (não rodar instâncias concorrentes)
npx playwright test --reporter=list  # E2E (quando aplicável)
```

Exemplos comuns de análise estática em TypeScript/Angular (ESLint/SonarJS/SonarQube):
- `typescript:S2933` — propriedade de classe nunca reatribuída → marcar como `readonly`.
- `typescript:S1854` — atribuição morta (dead store) → remover variável não utilizada.
- `typescript:S6544` — `Promise` retornada sem `await` ou tratamento.
