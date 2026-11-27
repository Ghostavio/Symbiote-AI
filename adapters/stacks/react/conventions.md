# Adaptador de Stack — React

Convenções recomendadas para projetos **React** acoplados ao **Symbiote-AI**. Ao aplicar este adaptador via `simbiose`, incorpore apenas o que se alinha à versão do React (18/19), ao meta-framework (Vite SPA, Next.js App Router, React Router/Remix, etc.), ao gerenciador de pacotes e às bibliotecas reais do projeto host no `.claude/PROJECT_REFERENCE.md`.

## Padrões de componentes e Hooks

- **Componentes funcionais com TypeScript estrito:** prefira `strict: true`, tipagem explícita de props e contratos de domínio (evite `any` injustificado e mutação direta de props ou estado).
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
- **Acessibilidade e testabilidade:** prefira HTML semântico (`<button>`, `<a href>`, `<label htmlFor>`), garanta `aria-label` em botões de ícone e controles sem texto visível, suporte navegação por teclado/foco em diálogos e menus, e use `data-testid` apenas como complemento estável quando seletores acessíveis não bastarem (nunca acoplar testes a classes CSS).

## Testes

### Unitários e de componentes (Vitest ou Jest + React Testing Library)

- **Teste comportamento, não implementação:** prefira queries acessíveis (`getByRole`, `getByLabelText`, `findByText`) e `userEvent` em vez de inspecionar estado interno de hooks ou detalhes do DOM.
- **Isolamento e mocks:** prefira `vi.fn()` / `jest.fn()` e mocks de fronteira HTTP (ex.: MSW) em vez de mockar internos do React; restaure mocks/timers entre testes para evitar vazamento de estado.

> Se o projeto host usar Jest ou outro runner/gerenciador (`pnpm`, `yarn`, `bun`), registre os comandos reais no `.claude/PROJECT_REFERENCE.md`.

### E2E (Playwright)

Siga [`docs/e2e.md`](../../../docs/e2e.md) para Page Object Model (POM), seletores acessíveis/`data-testid` e fixtures de autenticação.

## Preferências de editor (opcional)

O arquivo [`editor-settings.json`](editor-settings.json) traz overrides com escopo restrito por linguagem (`[typescriptreact]`, `[javascriptreact]`, `[typescript]`, `[javascript]`, `[css]`) para Prettier e ESLint. Mescle em `.cursor/settings.json` apenas mediante aprovação no plano de integração.
