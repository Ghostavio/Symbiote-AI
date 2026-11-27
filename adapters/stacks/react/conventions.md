# Adaptador de Stack — React

Convenções recomendadas para projetos **React** acoplados ao **Symbiote-AI**. Ao aplicar este adaptador via `simbiose`, incorpore apenas o que se alinha à versão do React (18/19), ao meta-framework (Vite SPA, Next.js App Router, React Router/Remix, etc.), ao gerenciador de pacotes e às bibliotecas reais do projeto host no `.claude/PROJECT_REFERENCE.md`.

## Padrões de componentes e Hooks

- **Componentes funcionais e tipagem (quando o projeto usar TypeScript):** prefira `strict: true`, tipagem explícita de props e contratos de domínio (evite `any` injustificado e mutação direta de props ou estado). Em projetos JavaScript, mantenha contratos claros de props e validação nas fronteiras externas.
- **Regras dos Hooks:** nunca chame Hooks condicionalmente, em loops ou após retornos antecipados; respeite `eslint-plugin-react-hooks` (`rules-of-hooks` e `exhaustive-deps`) sem silenciar alertas sem justificativa documentada.
- **Estado mínimo e derivado:** calcule valores derivados durante o render em vez de duplicar estado sincronizado via `useEffect`; prefira `useState`/`useReducer` locais antes de elevar para Context ou store global.
- **`useEffect` apenas para sincronização externa:** use efeitos somente para integrar com sistemas fora do React (assinaturas, timers, eventos de browser, SDKs externos), sempre retornando função de cleanup (incluindo `AbortController` para cancelar requisições manuais). Lógica disparada por ações do usuário pertence a event handlers, não a efeitos.
- **Imutabilidade e chaves estáveis:** atualize arrays/objetos de forma imutável e use `key` estável baseada em identificador único de domínio (nunca índice de array em listas dinâmicas, filtráveis ou reordenáveis).
- **React 19 e Server Components (quando aplicável):** em projetos com RSC (ex.: Next.js App Router), mantenha componentes como Server Components por padrão e restrinja `'use client'` à menor fronteira interativa necessária; evite `forwardRef` legado quando a versão do React suportar `ref` como prop direta.

## Gerenciamento de estado (servidor vs cliente)

- **Estado de servidor (dados remotos/cache):** utilize a camada adotada pelo projeto (ex.: TanStack Query, SWR, data loaders ou Server Actions) com chaves de cache consistentes, invalidação explícita e tratamento de estados de carregamento, vazio e erro — evite reimplementar fetch + cache manual em `useEffect`.
- **Estado de cliente e navegação:** mantenha estado de UI próximo do componente que o consome; use URL/search params para filtros, paginação e abas compartilháveis; reserve Context ou stores globais (ex.: Zustand, Redux Toolkit) para estado realmente transversal, cuidando para não provocar re-renders em cascata com valores não memoizados em `Provider`.

## Organização por feature (referência)

Quando o projeto organizar o código por módulos de feature, mantenha o domínio desacoplado de JSX/DOM:

```text
src/features/<feature>/
├── api/         # Clientes HTTP, DTOs, mappers e hooks de query/mutation
├── components/  # Componentes de UI específicos da feature
├── hooks/       # Custom hooks da feature
├── model/       # Tipos de domínio, regras puras e formatadores
└── pages/       # Telas/rotas lazy-loaded (ou app/<rota>/ em roteamento por arquivos)
```

- **Regras puras (`model/`):** sem dependência de React/DOM ou `fetch`, facilitando testes unitários rápidos e reutilização.
- **Camada de dados (`api/`):** isola contratos HTTP, DTOs, validação de payload e mapeamento para tipos de domínio.
- **Compartilhados (`src/shared/` ou `src/components/ui/`):** componentes reutilizáveis, hooks genéricos e utilitários ficam centralizados em vez de duplicados entre features.
- **Code-splitting e resiliência:** aplique `React.lazy` + `<Suspense>` (ou divisão automática por rota do framework) em telas pesadas e proteja fluxos críticos com Error Boundaries.

## Estilização, idioma e acessibilidade

- **Idioma da UI:** siga o idioma configurado no projeto (padrão pt-BR com acentuação correta).
- **Estilização e temas:** siga a estratégia já adotada no projeto (Tailwind CSS, CSS Modules, design system/tokens CSS), preservando consistência em modo claro/escuro quando suportado.
- **Acessibilidade e testabilidade:** prefira HTML semântico (`<button>`, `<a href>`, `<label htmlFor>`), garanta `aria-label` em botões de ícone e controles sem texto visível e suporte navegação por teclado/foco em diálogos e menus. Para atributos `data-testid`, siga a convenção de seletores adotada pelo projeto nos testes E2E (nunca acoplar testes a classes CSS).

## Testes e comandos

### Comandos do projeto

React não implica automaticamente TypeScript, Vitest ou Playwright. Preencha `<LINT_CMD>`, `<TYPECHECK_CMD>`, `<TEST_CMD>`, `<E2E_CMD>`, `<BUILD_CMD>` e `<DEV_CMD>` no `.claude/PROJECT_REFERENCE.md` **apenas com os scripts e ferramentas realmente instalados e confirmados no projeto host** (ex.: `package.json` + gerenciador de pacotes do repo). Evite comandos via `npx` sem `--no-install` que possam baixar pacotes fora do lockfile em execuções não interativas.

### Unitários e de componentes (Vitest ou Jest + React Testing Library)

- **Teste comportamento, não implementação:** em testes de componentes, prefira queries acessíveis (`getByRole`, `getByLabelText`, `findByText`) e `userEvent` em vez de inspecionar estado interno de hooks ou detalhes do DOM.
- **Isolamento e mocks:** prefira `vi.fn()` / `jest.fn()` e mocks de fronteira HTTP (ex.: MSW) em vez de mockar internos do React; restaure mocks/timers entre testes para evitar vazamento de estado.

### E2E (Playwright ou runner adotado pelo projeto)

Diferencie a estratégia de seletores entre testes de componentes (queries acessíveis) e E2E (siga sempre a convenção adotada pelo projeto): em projetos que adotam [`docs/e2e.md`](../../../docs/e2e.md), use Page Object Model (POM), `data-testid` (`page.getByTestId(...)`) como seletor principal e fixtures de autenticação — nunca seletores acoplados a classes CSS. Caso o projeto já utilize outra convenção (ex.: seletores acessíveis no Playwright ou outro runner), registre-a no `.claude/PROJECT_REFERENCE.md`.

## Preferências de editor (opcional)

O arquivo [`editor-settings.json`](editor-settings.json) traz overrides com escopo restrito por linguagem (`[typescriptreact]`, `[javascriptreact]`, `[typescript]`, `[javascript]`, `[css]`) para Prettier e ESLint. Mescle em `.cursor/settings.json` apenas mediante aprovação no plano de integração.
