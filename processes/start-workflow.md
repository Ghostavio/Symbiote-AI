---
name: start-workflow
description: "Use quando o usuário iniciar uma nova sessão de desenvolvimento — seja Nova Feature, Bug Fix, Follow-up, Melhoria/Refatoração, Testes, Express (mudança pequena) ou Freestyle."
---

# Start Workflow — Iniciar Sessão de Desenvolvimento

Ponto de entrada para sessões de desenvolvimento assistido por IA. Escolha o fluxo conforme o risco e o escopo. Use as verificações do projeto e acione revisão independente, documentação, tracker e time tracking quando forem relevantes para a entrega.

> **Stack de exemplo.** Os comandos e caminhos abaixo usam um stack de exemplo (Angular + Vitest + Playwright, tracker Azure DevOps). Rode a skill **`/integrar`** para adaptar comandos, caminhos e ferramentas ao SEU projeto. Onde lê-se "o tracker", entenda a ferramenta configurada (Azure DevOps, Jira, GitHub Issues…).

---

## Princípios — lições de desenvolvimento assistido por IA

Estes princípios moldam todos os fluxos abaixo. Detalhe e contexto em [`docs/aprendizados.md`](../docs/aprendizados.md).

1. **Edições em documentos gerados pela IA passam pelo orquestrador.** Editar manualmente um spec/design/plano deixa o orquestrador com uma versão velha em contexto e ele "corrige" suas mudanças. Peça a edição ao orquestrador — ou avise explicitamente o que mudou e por quê.
2. **Higienize o codebase antes da implementação assistida.** Código morto/artefatos não usados poluem discovery, design e implementação — a IA trata tudo que encontra como relevante e propaga o ruído.
3. **Nunca rode reviewer em background sobre arquivos que você está editando**, nem rode testes concorrentes (muitos runners — ex. Vitest — não suportam instâncias paralelas no mesmo projeto). Sequencial, ou isolado com lista explícita de arquivos a não tocar.
4. **Code review por subagente dedicado após cada fase** — o orquestrador tende a revisar superficialmente. O mesmo reviewer deve corrigir o que não exige decisão do usuário.
5. **Após 2-3 tentativas falhas num ajuste visual/CSS, pare e delegue** a um subagente com validação visual (Playwright MCP) e o histórico das tentativas falhas.
6. **Escolha o porte do fluxo pelo tamanho da demanda:** subagentes para trabalho grande (>50 arquivos); execução inline (**Fluxo Express**) para mudanças pequenas (<20 arquivos) — economiza tokens e cerimônia.
7. **Cole o texto da task no prompt do subagente** em vez de mandá-lo ler um plano gigante — ele lê o arquivo inteiro e gasta contexto à toa.
8. **Planeje um passo de integração explícito** entre fases paralelas com dependências cruzadas (worktrees são cópias isoladas; TODOs de uma fase não se resolvem na outra).
9. **Dados mock devem passar nas regras de negócio do projeto** (validadores de CPF/CNPJ/email…). Cruze mock × validators no review.
10. **Lint + typecheck ANTES da suíte de testes** — feedback de 3-12s contra 55-75s.
11. **Roteie o modelo por complexidade** (ver Passo 1.5): o mais capaz para orquestração, design e review; modelos rápidos (Sonnet) para tasks mecânicas bem especificadas. A estratégia é escolhida no início da sessão, não fixada em "sempre Opus".
12. **Diário de implementação incremental, não retroativo** — atualize a cada entrega, não no fim.
13. **Sincronize o tracker proativamente, não retroativamente** — crie/atualize work items durante a implementação.

---

## Passo 1 — Escolher fluxo

> Qual tipo de trabalho você vai realizar nesta sessão?
>
> **(a)** Implementar Nova Feature — spec → design → plano → implementação completa
> **(b)** Corrigir Bug — investigação, reprodução, correção, post-mortem
> **(c)** Follow-up / Polimento — continuar feature existente, iterar sobre follow-ups documentados
> **(d)** Melhoria / Refatoração — migração incremental, refatoração de módulo, melhoria técnica
> **(e)** Testes — adicionar/melhorar cobertura de testes unitários e/ou E2E
> **(g)** **Express** — mudança pequena e direta (tweak, ajuste, micro-feature): fluxo enxuto, sem spec/design formais
> **(f)** Freestyle — sessão livre com todas as integrações disponíveis

### Express vs. Completo — como escolher

| Sinais | Fluxo recomendado |
|---|---|
| < ~20 arquivos, escopo claro, 1 sessão, baixo risco | **(g) Express** |
| Ambíguo, multi-fase, > ~50 arquivos, alto risco, precisa de design | **(a) Nova Feature** (subagentes) |
| Bug isolado e claro | **(g) Express** ou **(b) Bug** conforme complexidade |

Na dúvida entre Express e Completo, pergunte ao usuário. Express prioriza velocidade e baixo consumo de tokens; Completo prioriza rigor e rastreabilidade para trabalho grande.

## Passo 1.5 — Estratégia de modelo dos subagentes

Pergunte ao usuário (uma vez, no início da sessão) como escolher o modelo ao despachar subagentes — em vez de usar sempre o mais caro:

> Como devo escolher o modelo dos subagentes nesta sessão?
> **(a) Adaptativo (recomendado)** — eu decido por complexidade: Sonnet para tasks mecânicas, Opus para as complexas/críticas.
> **(b) Sempre Opus** — máxima qualidade, maior custo.
> **(c) Sempre Sonnet** — máxima economia/velocidade.

Guarde a escolha para a sessão e respeite overrides pontuais do usuário.

### Heurística de roteamento (modo Adaptativo)

Classifique cada subagente **antes** de despachar e anuncie a escolha (ex.: "despachando em Sonnet — task mecânica"):

**→ Sonnet (mecânico / bem especificado):**
- Boilerplate seguindo padrão existente (entities, DTOs, mappers, barrels)
- Edições repetitivas em muitos arquivos (renomes, formatação, migração simples)
- Testes unitários diretos a partir de um plano detalhado
- Extração/sumarização de informação já estruturada

**→ Opus (complexo / alto impacto):**
- **Code review** e **design técnico** (sempre — decisões propagam para todas as fases)
- **Orquestração** (o thread principal)
- Lógica de negócio não-trivial, integração entre camadas, algoritmos
- Depuração de causa raiz, ajustes visuais difíceis, decisões de arquitetura
- Qualquer task ambígua ou com requisitos incompletos

Na dúvida sobre a complexidade, **suba o tier** (prefira Opus) — o custo de retrabalho supera o de tokens.

### Claude Code — sugerir `ultracode` em alta complexidade

No **Claude Code**, quando a task for de **alta complexidade** — feature grande multi-fase (>50 arquivos), migração/auditoria ampla, espaço de design largo, ou que se beneficie de verificação adversarial — **sugira ao usuário ativar o `ultracode`** (orquestração multi-agente via workflows). O ultracode decompõe o trabalho em muitos subagentes paralelos com verificação adversarial e síntese — ideal para abrangência e confiança em escala. É **opt-in** e consome muito mais tokens: proponha, estime o ganho e deixe o usuário decidir. Para trabalho pequeno/médio, mantenha a execução normal (Express inline ou subagentes pontuais).

## Passo 2 — Vincular Work Item

Invocar a skill **`create-work-item`** (em [`processes/create-work-item.md`](create-work-item.md)). Todos os fluxos passam por aqui para garantir rastreamento no tracker. No Express, isso pode ser uma única task leve (ver Fluxo G).

## Passo 3 — Registrar start time da sessão

Registrar a data e hora atual como start time da sessão no diário de implementação. O timetracking detalhado (7pace/tracker) é feito **incrementalmente** durante as entregas — não acumule para o fim (Princípio 12 e 13). A cada entrega: registrar start/end no diário, criar/atualizar a task no tracker via MCP e sincronizar com 7pace via `scripts/sync-7pace.sh`.

## Passo 4 — Executar fluxo selecionado

---

## Fluxo A: Implementar Nova Feature

Segue o workflow completo documentado em [`docs/workflow.md`](../docs/workflow.md).

### A.1 — Definir módulo

> Qual será o nome do módulo para esta feature?
> - **(a)** Usar módulo existente — qual?
> - **(b)** Criar novo módulo — qual nome? (criado na estrutura de módulos do projeto)

Se novo, criar a estrutura de pastas conforme a convenção do projeto (`docs/`, `domain/`, `data/`, `presentation/`).

### A.2 — Spec

Invocar a skill **`spec-builder`** para construir a especificação da feature interativamente. Se houver protótipo no Figma, invocar antes a skill **`figma-requirements`** para extrair requisitos do design.

### A.3 — Discovery → Brainstorm → Design → Plano → Implementação

Seguir as etapas do `docs/workflow.md`:
1. **Discovery** do codebase → `docs/discovery.md`
2. **Brainstorm** com o usuário → `docs/brainstorm/brainstorm-decisoes.md`
3. **Design técnico** via subagente → `docs/design/design-tecnico.md`
4. **Plano de implementação** via subagente → `docs/plano-implementacao.md` — **marque explicitamente quais tasks são "integração" e quais são "implementação pura"** (Princípio 8). Para cada task, use [`templates/story.template.md`](../templates/story.template.md) (contexto embutido — Princípio 7)
5. **Implementação** em fases com subagentes — agrupe tasks relacionadas num subagente grande e **cole o texto da task no prompt** (Princípios 6 e 7)
6. **Code review** obrigatório por subagente dedicado após cada fase (skill `phase-code-review`), que também corrige o que não exige decisão do usuário (Princípio 4)
7. **Timetracking** incremental no diário + 7pace; **tracker** sincronizado via MCP a cada fase (Princípios 12 e 13)

### A.4 — Conclusão

Este fluxo tipicamente é seguido pelo **Follow-up / Polimento** antes do merge. Informar ao usuário:

> Feature implementada. Próximos passos recomendados:
> - Nova sessão `/start-workflow` → Follow-up / Polimento para ajustes finais
> - Ou criar o PR quando estiver pronto

---

## Fluxo B: Corrigir Bug

### B.1 — Coletar informações

Perguntar ao usuário **uma pergunta por vez**:

1. **Área/Módulo/Componente afetado**
2. **Como reproduzir** — passos detalhados
3. **Comportamento atual** (incorreto)
4. **Comportamento desejado**
5. **Anexos** — screenshots, logs, stack traces
6. **Ambientes afetados** — local, staging, produção?
7. **Informações adicionais** — regressão recente, frequência, workaround

### B.2 — Avaliar complexidade e documentar

- **Simples** (1-2h): bug isolado, causa provável clara → correção direta
- **Moderado** (2-4h): múltiplos componentes, causa incerta → investigação
- **Complexo** (4h+): sistêmico, causa raiz desconhecida → debugging profundo

Criar documento `docs/bugs/bug-[work-item-id]-[nome-curto].md` com tudo coletado.

### B.3 — Investigar e reproduzir

1. **Ler arquivos relacionados** — componentes, services, templates
2. **Reproduzir com Playwright MCP** — navegar à página, executar passos, capturar screenshot do estado incorreto
3. **Invocar `superpowers:systematic-debugging`** se a causa não for óbvia (Superpowers é multi-plataforma — Claude Code, Cursor, Codex, Copilot CLI, Gemini CLI, OpenCode; ver https://github.com/obra/superpowers)
4. **Testar hipóteses** — para cada hipótese: aplicar correção → validar com Playwright MCP (screenshot antes/depois) → rodar testes → se falhou, reverter e tentar a próxima
5. **Escalar para MRE (Minimal Reproducible Example)** se após 5+ hipóteses a causa raiz continuar elusiva — ambiente mínimo que reproduza o problema, adicionando camadas até identificar a causa. Documentar o MRE no documento do bug.

### B.4 — Corrigir e validar

1. Aplicar a correção definitiva
2. **Adicionar testes** que cobrem o cenário do bug (unitário e/ou E2E)
3. Invocar **`phase-code-review`** para review completo
4. Validar visualmente com Playwright MCP

### B.5 — Documentar post-mortem

Criar/atualizar `docs/post-mortem/[work-item-id]-[nome-curto].md`:

```markdown
# Post-Mortem: [Título do Bug]
**Data:** [data]  **Work Item:** #[ID]  **Severidade:** [Simples/Moderado/Complexo]
## Problema
## Causa raiz
## Correção
## Testes adicionados
## Lições aprendidas
```

### B.6 — Criar PR

Antes: rodar a [validação pré-PR](#validação-pré-pr). Criar Pull Request via `gh`:

> Após `gh pr create` retornar com sucesso, mover a US/Bug para a coluna de
> revisão do tracker. Exemplo Azure DevOps (mantém `System.State` = `Active`,
> muda só o `System.BoardColumn`):
>
> ```
> wit_update_work_item({
>   id: <US_ID>,
>   updates: [{ op: "replace", path: "/fields/System.BoardColumn", value: "Waiting PR Approve" }]
> })
> ```

```bash
gh pr create --title "[Work Item ID] - [título curto]" --body "$(cat <<'EOF'
### Contain
- [x] Bugfix
- [x] Tests
### Details
* Fix [descrição da correção]
* Add [testes adicionados]
### Task
Task [título](https://<AZURE_ORG>.visualstudio.com/<AZURE_PROJECT>/_workitems/edit/[ID])
## Post-Mortem
[resumo da causa raiz e correção]
EOF
)"
```

---

## Fluxo C: Follow-up / Polimento

### C.1 — Identificar feature e documentos existentes

> Qual feature você está continuando? Informe o nome do módulo.

Ler `docs/relatorio-implementacao-*.md` (seção de follow-up), `docs/diario-implementacao.md` (últimas entradas) e o spec original. Apresentar os items documentados como pendentes e perguntar quais endereçar.

### C.2 — Criar plano de polimento

Com base nos items selecionados, criar plano para esta sessão.

### C.3 — Implementar

Mesmo ciclo do workflow: subagentes → code review → timetracking → tracker.

### C.4 — Criar PR

Antes: rodar a [validação pré-PR](#validação-pré-pr). Criar PR via `gh` seguindo o template do projeto (se houver, ex. `.github/PULL_REQUEST_TEMPLATE/`). Incluir referência ao work item e items endereçados.

> Após `gh pr create`, mover a US para a coluna de revisão do tracker (exemplo Azure DevOps no Fluxo B.6).

---

## Fluxo D: Melhoria / Refatoração

### D.1 — Definir escopo

1. **O que será melhorado/refatorado?** 2. **Motivação** 3. **Áreas afetadas** 4. **Risco** 5. **Referências**

### D.2 — Inventário de testes existentes

Antes de qualquer mudança, levantar cobertura atual (ex.):

```bash
find <src>/modules/[modulo] -name "*.spec.ts" | wc -l   # unitários
find <e2e-dir> -name "*.spec.ts" | wc -l                # E2E
```

Se a cobertura for insuficiente, **criar testes ANTES da refatoração** (caracterização): escrever testes que validam o comportamento atual, confirmar que passam, e só então refatorar — os testes devem continuar passando após cada etapa. Para E2E, seguir [`docs/e2e.md`](../docs/e2e.md) (Page Object Model, `data-testid`, fixture de auth, AAA).

### D.3 — Implementar incrementalmente

Para cada módulo/componente: validar estado atual (Playwright MCP) → aplicar mudança → rodar testes → validar visualmente → code review (`phase-code-review`) → se gerou correções, re-rodar testes e revalidar → commitar (um commit por módulo, só após review limpo).

### D.4 — Documentar

`docs/refatoracao/[work-item-id]-[nome].md`: escopo original vs. realizado, módulos afetados, testes adicionados, métricas antes/depois.

### D.5 — Criar PR

Antes: [validação pré-PR](#validação-pré-pr). Criar PR via `gh`. Para refatorações que decompõem PRs grandes, criar PRs menores por módulo quando possível.

> Após `gh pr create`, mover o(s) work item(s) para a coluna de revisão do tracker.

---

## Fluxo E: Testes

### E.1 — Definir escopo

> **(a)** Unitários **(b)** E2E **(c)** Ambos — e o que deseja testar?

### E.2 — Identificar prioridades

Levantar cobertura e gaps (ex.):

```bash
find <src> -name "*.component.ts" | while read f; do
  spec="${f%.ts}.spec.ts"; [ ! -f "$spec" ] && echo "SEM TESTE: $f"
done
```

Priorizar: **Crítico** (fluxos de negócio, ações destrutivas, validações) → **Importante** (lógica, services, guards, pipes) → **Nice-to-have** (apresentação simples).

### E.3 — Implementar testes

Seguir os padrões de teste do projeto. Para E2E, seguir [`docs/e2e.md`](../docs/e2e.md) (POM, `data-testid`, fixture de auth, AAA). Após cada batch: rodar a suíte completa e code review via `phase-code-review`.

### E.4 — Documentar métricas

No diário: testes adicionados (por tipo), cobertura antes/depois, fluxos críticos cobertos, gaps restantes.

### E.5 — Criar PR

Antes: [validação pré-PR](#validação-pré-pr). Criar PR focado nos testes adicionados.

---

## Fluxo G: Express (mudança pequena)

Fluxo **enxuto** para mudanças pequenas e de escopo claro (< ~20 arquivos): tweaks, ajustes de UI, micro-features, correções óbvias. Execução **inline** (sem fan-out de subagentes, sem spec/design formais) — economiza tokens e cerimônia, mantendo as salvaguardas essenciais.

### G.1 — Capturar a intenção

> O que precisa ser feito? (1-2 frases) E qual o critério de pronto?

Criar **uma** task leve no tracker (skill `create-work-item`, modo rápido) ou anotar no diário. Não gerar spec/design/discovery formais.

### G.2 — Confirmar que é mesmo "express"

Se ao explorar o escopo crescer (ambiguidade, > ~20 arquivos, decisões de design, risco alto), **pare e proponha migrar** para o Fluxo A/B/D. Não force trabalho grande no fluxo enxuto.

### G.3 — Implementar inline

1. Se for feature/bugfix com lógica, **escreva o teste primeiro** (`superpowers:test-driven-development`) e depois a implementação.
2. Higienize o que tocar (Princípio 2). Mantenha o diff focado.
3. Para ajuste visual: valide com Playwright MCP (screenshot). Se travar em 2-3 tentativas, **delegue a um subagente** com o histórico (Princípio 5) — é a única situação em que o Express despacha subagente.

### G.4 — Verificar (ordem importa — Princípio 10)

```bash
yarn lint            # 1. lint
npx tsc --noEmit     # 2. typecheck
yarn ng test <alvo>  # 3. testes (escopados ao que mudou)
```

Review leve pelo próprio orquestrador é aceitável no Express; para qualquer trecho com lógica de negócio não-trivial, ainda assim invoque `phase-code-review`.

### G.5 — Concluir

Commit pequeno e descritivo. Sincronizar a entrada de tempo (`scripts/sync-7pace.sh`) e atualizar a task no tracker. Criar PR via `gh` se aplicável (rodar a [validação pré-PR](#validação-pré-pr) antes).

---

## Fluxo F: Freestyle

### F.1 — Priming de contexto

> **Sessão Freestyle iniciada.** Integrações disponíveis:
>
> **Skills:** `/spec-builder`, `/phase-code-review`, `/figma-requirements`, `/create-work-item`, `/integrar`
> **MCP Servers:** Azure DevOps (`mcp__azure-devops__*`) ou Jira, SonarQube quando configurado (`mcp__sonarqube__*`), Playwright (`mcp__plugin_playwright_playwright__*`)
> **Scripts:** `scripts/sync-7pace.sh`
> **Referências:** [`templates/project-reference.template.md`](../templates/project-reference.template.md), [`docs/workflow.md`](../docs/workflow.md), [`docs/aprendizados.md`](../docs/aprendizados.md)
>
> O que você gostaria de fazer?

### F.2 — Iterar com o usuário

O orquestrador oferece, conforme o contexto: code review com análise estática local ao modificar código; timetracking no diário ao concluir fases; validação visual com Playwright ao mexer em UI; sincronização com o tracker quando work items forem relevantes.

### F.3 — Concluir

> **(a)** Criar PR **(b)** Apenas commitar e pushar **(c)** Encerrar sem ação

Se (a): rodar a [validação pré-PR](#validação-pré-pr) e criar PR via `gh`; mover o(s) work item(s) para a coluna de revisão do tracker.

---

## Validação pré-PR

**Aplicável a todos os fluxos** (B.6, C.4, D.5, E.5, F.3, G.5). Antes de criar o PR, rode a suíte crítica e confira o estado do repositório:

```bash
yarn ng test --watch=false        # testes
npx playwright test               # E2E (se relevante)
yarn lint                         # lint
npx tsc --noEmit                  # typecheck
git status                        # estado da árvore
git diff --stat origin/<main>...HEAD
```

Confirmar: exit codes 0; `git status` mostra só o esperado (sem órfãos como `.env`, PNGs de debug, `.DS_Store`); `git diff --stat` bate com o escopo do work item.

> **Compressão de saída (ex. RTK).** Se você usa um proxy que comprime saídas de Bash (ex. RTK — Rust Token Killer), há risco residual da heurística esconder algo. Rode esta suíte em modo passthrough cru (ex.: `rtk proxy <cmd>`) antes do PR. Sem esse proxy, este passo é redundante (a saída já é crua) — pular.

---

## Passo Final — Encerrar sessão

1. **Registrar end time da sessão** — `git log -1 --format="%ai"` para marcar o final no diário
2. **Verificar entregas pendentes** — se alguma entrega não foi sincronizada com 7pace/tracker durante a sessão, sincronizar agora
3. **Atualizar diário** com resumo (total de entregas, duração, observações)
