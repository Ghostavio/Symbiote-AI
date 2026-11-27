# Review Checks — Adaptador React

Checklist especializado para carregar em [`processes/phase-code-review.md`](../../../processes/phase-code-review.md) (§2, §3, §4, §5 e §7–§8) quando o adaptador `react` estiver acoplado ao projeto.

## §2 Code Quality & Patterns (React)

- [ ] Componentes funcionais bem estruturados; quando o projeto usar TypeScript, tipagem estrita sem `any` injustificado e sem mutação direta de props ou estado.
- [ ] Regras dos Hooks respeitadas (`rules-of-hooks` e `exhaustive-deps` sem `eslint-disable` sem justificativa clara).
- [ ] Estado derivado calculado durante o render em vez de duplicado e sincronizado via `useEffect`.
- [ ] `useEffect` restrito a sincronização com sistemas externos (não usado para derivar estado ou responder a eventos do usuário).
- [ ] `key` estável e única em listas renderizadas (sem índice de array em listas dinâmicas, filtráveis ou reordenáveis).
- [ ] Em projetos com Server Components (RSC), `'use client'` aplicado apenas nas fronteiras interativas necessárias, sem importar módulos server-only no cliente.
- [ ] Sem imports não utilizados, código morto ou `console.log` em código de produção.

## §3 Architecture & Layer Consistency (React)

- [ ] Regras de domínio/formatação mantidas puras e separadas de componentes de apresentação e acesso HTTP.
- [ ] Estado de servidor tratado pela estratégia configurada no projeto (ex.: TanStack Query, SWR, loaders/Server Actions) sem duplicação manual de cache em stores ou `useEffect`.
- [ ] Componentes, hooks e utilitários reutilizáveis centralizados na camada compartilhada (sem duplicação entre features).
- [ ] Rotas/telas pesadas com code-splitting (`React.lazy`/`Suspense` ou divisão por rota do framework) e protegidas pelas regras de autenticação/autorização da spec.
- [ ] Estados de carregamento, vazio e erro tratados explicitamente (com Error Boundaries em fluxos críticos quando aplicável).

## §4 Bug Detection (React)

- [ ] **Vazamento de memória / limpeza:** `useEffect` com listeners DOM, timers, WebSockets ou assinaturas sem função de cleanup correspondente.
- [ ] **Race conditions / closures obsoletas:** requisições manuais em `useEffect` sem `AbortController` ou guarda de cancelamento; atualizações baseadas no estado anterior sem forma funcional (`setState(prev => ...)`).
- [ ] **Loops infinitos de render:** objetos, arrays ou funções recriados a cada render incluídos nas dependências de `useEffect` que aciona `setState`.
- [ ] **Segurança:** risco de XSS via `dangerouslySetInnerHTML`, URLs dinâmicas em `href`/`src` sem validação de protocolo, ou segredos expostos em variáveis públicas de cliente (`VITE_*`, `NEXT_PUBLIC_*`, `REACT_APP_*`).
- [ ] **Performance:** valor de `Context.Provider` recriado a cada render causando re-renders em cascata; listas grandes ou cálculos custosos no render sem paginação, virtualização ou memoização justificada.

## §5 Accessibility & Tests (React)

- [ ] HTML semântico (`<button>` em vez de `<div onClick>`), `<label>` associado a inputs, `aria-label` em botões de ícone e suporte a foco/teclado em modais, menus e tabelas interativas.
- [ ] **Testes de componentes:** escritos com foco em comportamento (queries acessíveis da Testing Library e `userEvent`), cobrindo caminhos felizes, erro e estados vazios.
- [ ] **Testes E2E:** seguem a convenção de seletores adotada pelo projeto (`data-testid` / `getByTestId` quando usar `docs/e2e.md`, ou a convenção registrada em `.claude/PROJECT_REFERENCE.md`), sem acoplamento a classes CSS voláteis.

## §7–§8 Quality Checks & Static Analysis (exemplos condicionais React)

Execute **apenas** os scripts e ferramentas realmente instalados e confirmados no projeto host (`.claude/PROJECT_REFERENCE.md` / `package.json`). Evite invocar `npx` sem `--no-install` contra ferramentas ausentes (como `tsc`, `vitest` ou `playwright`), pois isso pode baixar pacotes fora do lockfile em revisões não interativas.

Exemplos condicionais (use os scripts reais do projeto com `npm`/`pnpm`/`yarn`/`bun`, somente quando a respectiva ferramenta estiver configurada):

```bash
npm run lint                                     # quando houver script de lint (ESLint com react-hooks/jsx-a11y/sonarjs)
npm run typecheck                                # ou ./node_modules/.bin/tsc --noEmit (somente se TypeScript estiver instalado)
npm test                                         # runner unitário/componentes configurado (ex.: Vitest ou Jest)
npm run test:e2e                                 # somente se Playwright ou outro runner E2E estiver configurado
```

Exemplos comuns de análise estática em TypeScript/React (ESLint / SonarJS / SonarQube):
- `react-hooks/exhaustive-deps` — dependência ausente ou instável em `useEffect`/`useMemo`/`useCallback`.
- `typescript:S6440` — chamada condicional de Hook violando as Rules of Hooks.
- `typescript:S6479` — uso de índice de array como `key` em listas React.
- `typescript:S6544` — `Promise` retornada sem `await` ou tratamento de erro (ex.: em handlers de evento).
