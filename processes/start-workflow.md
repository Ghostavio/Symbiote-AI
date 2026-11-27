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
4. **Dimensione a revisão pelo risco da fase.** Prefira uma revisão independente em entregas de alto impacto ou complexidade, quando disponível e autorizada. Aplique apenas correções que façam parte da entrega.
5. **Após 2-3 tentativas falhas num ajuste visual/CSS, pare e delegue** a um subagente com validação visual (Playwright MCP) e o histórico das tentativas falhas.
6. **Escolha o porte do fluxo pelo risco, escopo e reversibilidade.** A quantidade de arquivos ajuda a estimar o esforço. Uma mudança pequena em autorização ou cobrança ainda pode exigir revisão independente.
7. **Cole o texto da task no prompt do subagente** em vez de mandá-lo ler um plano gigante — ele lê o arquivo inteiro e gasta contexto à toa.
8. **Planeje um passo de integração explícito** entre fases paralelas com dependências cruzadas (worktrees são cópias isoladas; TODOs de uma fase não se resolvem na outra).
9. **Dados mock devem passar nas regras de negócio do projeto** (validadores de CPF/CNPJ/email…). Cruze mock × validators no review.
10. **Lint + typecheck ANTES da suíte de testes** — feedback de 3-12s contra 55-75s.
11. **Dimensione modelo e esforço conforme a tarefa.** Respeite as preferências do usuário e use os critérios do Passo 1.5 para sugerir ajustes quando houver ganho claro.
12. **Diário de implementação incremental, não retroativo** — atualize a cada entrega, não no fim.
13. **Sincronize o tracker proativamente, não retroativamente** — crie/atualize work items durante a implementação.

---

## Passo 1 — Escolher fluxo

Se o pedido já define o fluxo ou descreve uma mudança clara, fácil de verificar e de baixo risco, siga diretamente o fluxo adequado. Use o menu quando a intenção ainda não estiver clara.

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
| Escopo claro, baixo risco, mudança fácil de verificar e reverter | **(g) Express** |
| Escopo ambíguo, dependências entre fases, alto impacto ou decisões de design | **Fluxo completo** conforme o tipo de trabalho |
| Bug isolado e claro | **(g) Express** ou **(b) Bug** conforme complexidade |

No Express, vá direto ao [Fluxo G](#fluxo-g-express-mudança-pequena). Ele já cobre os passos de preparação aplicáveis.

## Passo 1.5 — Esforço e seleção de modelo

Use a preferência mais específica disponível: a escolha explícita para a tarefa, a preferência da sessão, o padrão documentado do projeto e, por fim, **medium** como padrão do kit. O usuário pode mudar o nível a qualquer momento. Uma tarefa simples segue com o padrão, sem iniciar um questionário.

| Esforço | Quando sugerir |
| --- | --- |
| `low` | Tarefa mecânica ou revisão de um diff pequeno, com critério de pronto claro e baixo impacto. |
| `medium` | Implementação ou revisão comum, com contexto conhecido e verificações disponíveis. |
| `high` | Regras de negócio complexas, investigação difícil, integrações ou mudanças com risco relevante de regressão. |
| `max` | Planejamento ou validação de alto impacto em várias áreas, quando a análise adicional justificar custo e latência. |

Quando o risco ou a complexidade indicar outro nível, explique brevemente qual tarefa se beneficia, por quê e qual a contrapartida. Use a preferência vigente até o usuário aceitar a sugestão, salvo se ele já tiver delegado os ajustes. A sugestão pode se aplicar só à etapa que dela precisa, como a orquestração de uma mudança ampla.

Trate **modelo** e **esforço** como escolhas separadas. Em Anthropic, OpenAI e Google, use o modelo escolhido pelo usuário ou pelo projeto e aplique o esforço aos controles disponíveis na ferramenta. Considere sugerir outro modelo separadamente quando houver benefício claro. Os quatro níveis são a escala do kit. Use o equivalente documentado pelo cliente, quando houver, e informe se a sessão não permitir alterar um parâmetro ou se for preciso ajustá-lo manualmente. Registre apenas o nível que de fato foi aplicado.

### Claude Code — sugerir `ultracode` em alta complexidade

No **Claude Code**, quando a task for de **alta complexidade** — feature grande multi-fase (>50 arquivos), migração/auditoria ampla, espaço de design largo, ou que se beneficie de verificação adversarial — **sugira ao usuário ativar o `ultracode`** (orquestração multi-agente via workflows). O ultracode decompõe o trabalho em muitos subagentes paralelos com verificação adversarial e síntese — ideal para abrangência e confiança em escala. É **opt-in** e consome muito mais tokens: proponha, estime o ganho e deixe o usuário decidir. Para trabalho pequeno/médio, mantenha a execução normal (Express inline ou subagentes pontuais).

## Passo 2 — Vincular Work Item

Quando o fluxo usar o tracker do projeto, invocar a skill **`create-work-item`** (em [`processes/create-work-item.md`](create-work-item.md)). O Express trata o vínculo no próprio fluxo.

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
6. **Code review** ao concluir cada fase (skill `phase-code-review`), com profundidade e correções conforme risco e escopo (Princípio 4)
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

Fluxo enxuto para mudanças claras, de baixo risco e fáceis de verificar, como ajustes de documentação, UI ou correções pontuais. Pode ser executado localmente em um projeto sem credenciais, MCPs ou setup global.

### G.1 — Capturar a intenção

Use o pedido e o contexto para identificar a mudança e o critério de pronto. Pergunte apenas sobre dúvidas que afetem o resultado. Reaproveite o ticket ou diário quando já fizer parte do projeto. Para uma mudança local, o resumo da entrega é suficiente.

### G.2 — Confirmar que é mesmo "express"

Reavalie o fluxo se a descoberta revelar risco alto, dependências entre fases ou decisões de design ainda em aberto. Explique o motivo e use o fluxo correspondente quando precisar de mais planejamento ou revisão independente.

### G.3 — Implementar inline

1. Para uma correção de comportamento, reproduza o problema. Use o framework de testes do projeto quando couber um teste de regressão.
2. Mantenha o diff focado no pedido.
3. Para ajuste visual, use o navegador ou a ferramenta visual disponível. Se a validação visual estiver indisponível, informe essa limitação.

### G.4 — Verificar

Identifique os comandos disponíveis na documentação, configuração ou CI do projeto. Rode as verificações relevantes para o diff, começando pelas rápidas quando isso ajudar a obter feedback. Revise o diff e os resultados. Se uma verificação aplicável não estiver disponível, informe a limitação.

### G.5 — Concluir

Resuma a mudança, as verificações executadas e eventuais limitações. Atualize o tracker ou registre horas quando a integração estiver configurada e a entrega pedir isso. Se a entrega incluir um PR, rode a [validação pré-PR](#validação-pré-pr).

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

**Aplicável a todos os fluxos** (B.6, C.4, D.5, E.5, F.3, G.5). Antes de criar o PR, rode as verificações relevantes da stack do projeto e confira o estado do repositório. Exemplo para Angular:

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

Para encerrar o Express, siga o passo G.5. Nos demais fluxos, use os passos abaixo conforme as integrações da sessão.

1. **Registrar end time da sessão** — `git log -1 --format="%ai"` para marcar o final no diário
2. **Verificar entregas pendentes** — se alguma entrega não foi sincronizada com 7pace/tracker durante a sessão, sincronizar agora
3. **Atualizar diário** com resumo (total de entregas, duração, observações)
