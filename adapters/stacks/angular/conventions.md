# Adaptador de Stack — Angular

Convenções recomendadas para projetos **Angular** acoplados ao **Symbiote-AI**. Ao aplicar este adaptador via `simbiose`, incorpore apenas o que se alinha à versão do Angular e às bibliotecas reais do projeto host (ajuste gerenciador de pacotes, biblioteca de UI e runner de testes no `.claude/PROJECT_REFERENCE.md`).

## Padrões de componentes e reatividade

- **Standalone components** por padrão (evitar novos `NgModule`).
- **`ChangeDetectionStrategy.OnPush`** em todos os componentes.
- **Injeção de dependências com `inject()`** (evitar injeção via construtor em código novo).
- **Angular Signals** para estado local e derivado (`signal()`, `computed()`, `input()`, `output()`, `model()`), evitando stores globais desnecessários.
- **Nova sintaxe de control flow** nos templates (`@if`, `@for` sempre com `track`, `@switch`).
- **Ciclo de vida RxJS seguro:** toda subscription manual deve usar `takeUntilDestroyed(this.destroyRef)` (ou `async` pipe / `toSignal()`).

## Arquitetura em camadas (referência Clean Architecture)

Quando o projeto adotar módulos de feature em camadas, preserve o fluxo e o isolamento de responsabilidades:

```text
modules/<feature>/
├── domain/      # Entidades, contratos/interfaces de gateway, use cases
├── infra/       # Gateways HTTP, DTOs, mappers
├── main/        # Fachadas / composição de dependências
└── view/        # Componentes, rotas lazy-loaded (loadChildren), guards
```

- **Domain / Use cases:** puros — sem chamadas HTTP diretas e sem dependências de UI.
- **Gateways / Infra:** abstraem detalhes de HTTP, DTOs e mapeamento de/para entidades de domínio.
- **Shared (`shared/`):** utilitários, componentes reutilizáveis, interceptors e pipes compartilhados ficam centralizados em vez de duplicados entre módulos.

## Estilização, idioma e acessibilidade

- **Idioma da UI:** siga o idioma configurado no projeto (padrão pt-BR com acentuação correta).
- **Theming / Dark mode:** use tokens CSS ou `:host-context(.dark-theme)` consistentemente nos componentes de UI quando o projeto suportar tema escuro.
- **Acessibilidade e testabilidade:** garanta `aria-label` em botões de ícone, tabelas e controles interativos, e `data-testid` em elementos testáveis (nunca acoplar testes a classes CSS).

## Testes

### Unitários (Vitest com `@angular/build:unit-test`)

Quando o projeto usar Vitest via `@angular/build:unit-test`:

- **Não usar:** `fakeAsync`/`tick`, `TestBed.initTestEnvironment()` ou `provideZonelessChangeDetection()` (se não aplicável à versão configurada).
- **Mocking:** prefira `vi.fn()`, `vi.mock()`, `spyOn` / mocks tipados.
- **Concorrência:** evite rodar múltiplas instâncias simultâneas de `ng test` / Vitest no mesmo workspace (causa timeouts e falhas espúrias).

> Se o projeto host ainda usar Jasmine/Karma ou Jest, registre o runner real no `.claude/PROJECT_REFERENCE.md` e adapte os comandos sugeridos.

### E2E (Playwright)

Siga [`docs/e2e.md`](../../../docs/e2e.md) para Page Object Model (POM), seletores por `data-testid` e fixtures de autenticação.

## Preferências de editor (opcional)

O arquivo [`editor-settings.json`](editor-settings.json) traz overrides com escopo restrito por linguagem (`[html]`, `[scss]`, `[css]`, `[typescript]`) para Prettier/ESLint, além de defaults de `angular-schematics`. Mescle em `.cursor/settings.json` apenas mediante aprovação no plano de integração e, se o projeto usar Vitest em subdiretório, adicione `vitest.rootConfig` com o caminho real do arquivo de configuração.
