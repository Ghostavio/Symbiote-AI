# Workflow de Implementação com AI

> Processo de desenvolvimento assistido por AI utilizado para implementar features no projeto com workflow Superpowers (multi-plataforma: Claude Code, Cursor, Codex, Copilot CLI, Gemini CLI, OpenCode) + subagent-driven-development.
> Este documento serve como referência para todas as novas implementações que adotem o mesmo padrão.

---

## 1. Visão Geral

```
Discovery → Brainstorm → Design → Plano → [Implementação → Code Review → Testes → Documentação] × N fases → Polimento → Relatório Final
```

O agente principal (orquestrador) coordena o trabalho, delegando implementação e reviews para subagentes dedicados. O orquestrador nunca implementa diretamente código extenso — sua função é planejar, despachar, revisar e documentar.

---

## 2. Modelo dos Subagentes

A orquestração, o design técnico e o code review usam sempre o **modelo mais capaz disponível** na ferramenta de AI em uso. Os demais subagentes (implementação, testes, tasks mecânicas) seguem a estratégia escolhida no início da sessão (Passo 1.5 de `processes/start-workflow.md`: Adaptativo, Sempre Opus ou Sempre Sonnet).

- **Claude Code:** Opus (`model: "opus"`) para orquestração, design e review; no modo Adaptativo, Sonnet (`model: "sonnet"`) para tasks mecânicas bem especificadas.
- **Cursor:** Opus / GPT-5 / Gemini 2.5 Pro (o mais capaz disponível no plano)
- **Codex / Antigravity:** o tier "max" / mais capaz da ferramenta
- **VSCode + Copilot:** o modelo mais capaz na seleção do agent mode

A qualidade do code review e do design depende fortemente do modelo. Não economizar aqui.

---

## 3. Etapas do Processo

### 3.1 Discovery (orquestrador)

Antes de qualquer produção de documentos, o orquestrador faz uma varredura do codebase:

1. Explorar arquitetura, padrões e convenções existentes (ver `docs/discovery.md`, modelo a preencher pelo projeto, como referência viva do codebase)
2. Produzir `docs/discovery.md` específico da feature contendo:
   - Lista de arquivos essenciais com caminhos completos
   - Trechos relevantes extraídos (rotas, sidebar, guards, services, componentes de referência)
   - Padrões e convenções que devem ser seguidos
3. Este documento é passado como referência para todos os subagentes subsequentes

### 3.2 Brainstorm (orquestrador + usuário)

Perguntas de clarificação uma a uma, propostas de abordagem com trade-offs, decisões documentadas em `docs/brainstorm/brainstorm-decisoes.md`.

### 3.3 Design Técnico (subagente)

Documento detalhado delegado a um subagente que lê spec + discovery + brainstorm. Cobre: estrutura de arquivos, entities, DTOs, mappers, gateways, use cases, facades, componentes, rotas, sidebar, mock server, testes.

### 3.4 Plano de Implementação (subagente)

Tasks granulares organizadas em fases com dependências explícitas e notas de paralelismo. Cada task lista arquivos exatos, código completo, comandos de teste e mensagem de commit.

### 3.5 Implementação (subagentes em paralelo)

Ver seção 4 abaixo.

### 3.6 Polimento (iterativo, orquestrador + subagentes)

Ajustes visuais e de UX feitos iterativamente com feedback do usuário. Usar **Playwright MCP** para validação visual antes de commitar ajustes CSS.

> **Importante:** o esforço de polimento que transforma o protótipo em interface pronta para produção deve viver em uma **User Story separada** (US de produção), conforme definido no padrão de prototipação descrito em `processes/create-work-item.md` e em `docs/processo-work-items.md`.

---

## 4. Implementação com Subagentes

### 4.1 Paralelismo com Worktrees

Para tasks independentes, despachar sub-agentes em paralelo com isolamento via git worktrees. Exemplo no Claude Code:

```
Agent({
  description: "FASE 1: Camada de domínio",
  model: "opus",
  isolation: "worktree",
  prompt: "..."
})
```

Em outras ferramentas, usar o mecanismo equivalente (Cursor Background Agents, sub-tasks no Codex/Antigravity) e criar manualmente o worktree (`git worktree add`) se a ferramenta não fizer isolamento automático.

- Cada worktree é uma cópia isolada do repositório
- Sem conflitos de git entre sub-agentes
- Após conclusão, cherry-pick dos commits para o branch principal

**Regras:**

- Worktrees paralelas devem ter escopos **estritamente disjuntos** (sem arquivos em comum)
- Se houver dependências cruzadas, planejar um **passo de integração** após o merge
- Nunca despachar múltiplas instâncias de `yarn ng test` simultaneamente

### 4.2 Prompt do Subagente Implementador

Cada subagente recebe:

1. **Task completa** — texto colado no prompt (não path para ler)
2. **Contexto** — quais arquivos já existem, dependências disponíveis
3. **Referências** — paths para discovery.md, design técnico, config.ts
4. **Regras** — OnPush, inject(), Signals, pt-BR, sem Co-Authored-By
5. **Commit** — mensagem em português

### 4.3 Agrupamento de Tasks

Agrupar tasks relacionadas em um único subagente ao invés de muitos pequenos:

- Reduz re-leitura de contexto (documentos de referência lidos uma vez)
- Ex: "FASE 1 inteira" (~85 arquivos) em um subagente é mais eficiente que 8 separados

### 4.4 Timetracking Automático via Diário

O orquestrador deve registrar **start time** e **end time** de cada fase diretamente no diário de implementação, usando timestamps reais para gerar timetracking preciso.

**Antes de despachar o subagente:**

1. Registrar a data e hora atual no diário como **start time** da fase:
   ```markdown
   ## FASE X: [nome]
   **Start:** 2026-01-14 14:00
   ```

**Após entrega + code review:**

2. Consultar o timestamp do último commit do subagente via `git log -1 --format="%ai"` para obter o **end time** real
3. Atualizar o diário com o end time e a duração calculada:
   ```markdown
   ## FASE X: [nome]
   **Start:** 2026-01-14 14:00
   **End:** 2026-01-14 16:00 (via git log)
   **Duração:** 2h 00min
   ```

**Por que:** Reconstruir timetracking retroativamente a partir de commits é trabalhoso e impreciso. Registrar start/end no momento da execução elimina esse problema e alimenta diretamente o timetracking consolidado e os work items do Azure DevOps.

**Para fases paralelas:** Registrar start de todas as fases antes de despachar, e end de cada uma conforme concluem.

---

## 5. Code Review

### 5.1 O que o reviewer faz

Ao concluir uma fase de implementação, use [`phase-code-review`](../processes/phase-code-review.md) para comparar a entrega com os requisitos e verificar o diff com os comandos do projeto. Ajuste a profundidade ao risco e use revisão independente para mudanças de alto impacto quando disponível e autorizada.

Pedidos de avaliação recebem achados e evidências. Durante uma implementação, aplique as correções dentro do escopo autorizado. Inclua correções em commit quando a entrega já prevê commit.

### 5.2 Como invocar

```
Invoke a skill phase-code-review após completar [FASE X].
```

Use o roteiro da skill na sessão atual ou envie-o a um reviewer autorizado.

### 5.3 Após o review

1. Ler o relatório do reviewer
2. Resolver issues escalados (que precisam de decisão do usuário)
3. **Registrar end time** — consultar `git log -1 --format="%ai"` para obter o timestamp do último commit e atualizar o diário com end time + duração (ver seção 4.4)
4. **Atualizar o diário de implementação** (`docs/diario-implementacao.md`) com resultados do review
5. **Sincronizar Board** (ver seção 5.4)
6. **Registrar horas no 7pace** (ver seção 5.5)
7. Prosseguir para a próxima fase

### 5.4 Sincronizar Board via Azure MCP

Após o code review e atualização do diário, sincronizar o Azure DevOps Board com o trabalho entregue na fase. Este passo é **obrigatório** quando o usuário forneceu um ID de Feature no spec.

**Pré-requisito:** O ID do Feature parent deve estar definido nos metadados do spec (seção 1, campo `Azure DevOps Feature ID`). Se não estiver, perguntar ao usuário antes da primeira sincronização.

**Fluxo:**

1. **Criar/atualizar work item da fase** no Azure DevOps via MCP, seguindo o padrão de hierarquia (Feature → User Story → Task) e os formatos definidos em `docs/processo-work-items.md` e na skill `processes/create-work-item.md`:

   ```
   mcp__azure-devops__wit_create_work_item({
     project: "<AZURE_PROJECT>",
     workItemType: "User Story",
     title: "FASE X: [descrição]",
     // ... campos
   })
   mcp__azure-devops__wit_add_child_work_items({
     parentId: [Feature ID],
     childIds: [work item criado]
   })
   ```

2. **Criar tasks** para cada ação concreta realizada na fase, no infinitivo (ex: "Criar serviço xpto", "Implementar tela xyz", "Realizar testes unitários", "Gerar evidência da estória")

3. **Registrar timetracking** no formato compatível com 7pace Timetracker:

   ```markdown
   | Start Date | Start Time | End Time | Activity Type   |
   | ---------- | ---------- | -------- | --------------- |
   | 2026-01-14 | 14:00      | 16:00    | Desenvolvimento |
   ```

4. **Atualizar estado** do work item para Done/Resolved

5. **Registrar IDs** no documento .md da fase para rastreamento bidirecional:
   ```markdown
   ### Task 3: Criar estrutura de pastas (Azure DevOps #1234)
   ```

**Quando o Feature ID não foi fornecido:** O orquestrador deve perguntar ao usuário se deseja criar work items no Board. Se não, pular esta etapa e registrar apenas no diário.

### 5.5 Registrar horas no 7pace Timetracker

Após atualizar o diário e o Board, registrar as horas no 7pace usando o script `scripts/sync-7pace.sh` (ou o wrapper opcional `.claude/integrations/timetracking/sync.sh`, para quem também registra no Clockify). Os timestamps vêm do diário (seção 4.4: start time registrado antes de despachar, end time via `git log`).

**Chamada:**

```bash
scripts/sync-7pace.sh \
  --description "FASE X: [nome da fase]" \
  --start "[start time ISO 8601 do diário]" \
  --end "[end time ISO 8601 do git log]" \
  --work-item-id [ID do work item no Azure DevOps] \
  --activity-type "Desenvolvimento"
```

**Activity types comuns no workflow:**
- `Desenvolvimento` — fases de implementação de código
- `Operação` — documentação, configuração, evidências
- `Reunião` — reuniões com stakeholders
- `Rituais Scrum` — dailies, planning, review, retro

**Pré-requisito:** `SEVENPACE_API_TOKEN` e `SEVENPACE_BASE_URL` exportados no shell (skill `/setup-7pace`). O `.claude/integrations/timetracking/.env` ainda funciona, mas só como fallback legado.

**Se o work item ainda não existe no Azure DevOps** (ex: seção 5.4 foi pulada), perguntar ao usuário:
- (a) Criar o work item agora via Azure MCP (`mcp__azure-devops__wit_create_work_item({ project: "<AZURE_PROJECT>", ... })`)
- (b) Informar o ID de um work item já criado manualmente
- (c) Pular — registrar apenas no diário de implementação, sem enviar ao 7pace

### 5.6 Regras Críticas

- **Revise cada fase com profundidade proporcional ao risco.**
- **Nunca despachar reviewer em background** enquanto faz alterações nos mesmos arquivos — o reviewer pode reverter seu trabalho
- **Nunca rodar testes concorrentemente** com outro agente — causa timeouts e falhas espúrias
- **Aplique correções somente no escopo autorizado.**
- **Se o reviewer encontra algo que precisa de decisão** → escala ao orquestrador → orquestrador pergunta ao usuário
- **Priorize verificações rápidas do projeto** quando ajudarem a antecipar falhas.

---

## 6. Testes

### 6.1 Testes Unitários (Vitest)

- Framework: Vitest com `@angular/build:unit-test`
- NÃO usar: `fakeAsync`/`tick`, `TestBed.initTestEnvironment()`, `provideZonelessChangeDetection()`
- Mocking: `vi.fn()`, `vi.mock()`, `MockedObject`, `spyOn`
- Sempre rodar `yarn lint` e typecheck ANTES dos testes unitários

### 6.2 Testes E2E (Playwright)

Seguir o documento **`docs/e2e.md`** para convenções detalhadas:

- Padrão **Page Object Model** (POM)
- Seletores via **`data-testid`** (nunca classes CSS)
- Fixture de autenticação em todos os testes
- Validação visual via **Playwright MCP** para ajustes de CSS

---

## 7. Documentação Contínua

### 7.1 Diário de Implementação (`docs/diario-implementacao.md`)

Atualizar **imediatamente** após cada fase com:

- Decisões tomadas e justificativas
- Descobertas sobre o codebase
- Bugs encontrados e como foram resolvidos
- Métricas (arquivos, testes, tempo)
- Lições aprendidas

### 7.2 Aprendizados (`docs/aprendizados.md`)

Quando algo inesperado acontece (bug, conflito, padrão novo), documentar como aprendizado com:

- **Problema** — o que aconteceu
- **Causa raiz** — por que
- **Solução** — como foi resolvido
- **Recomendação** — como evitar no futuro

### 7.3 Relatório Final (`docs/relatorio-implementacao-*.md`)

Ao final da implementação, consolidar:

- Implementado vs. Especificado (tabela completa)
- Decisões técnicas com justificativas
- Dificuldades e soluções
- Métricas finais
- Framework de follow-up (pendentes, bugs, melhorias, dívida técnica, checklist pré-produção)

---

## 8. Edições em Documentos

**Sempre solicitar que o agente orquestrador realize as edições** ao invés de editar manualmente. Se a edição manual for inevitável, informar explicitamente o orquestrador sobre o que foi alterado e por quê.

Motivo: o orquestrador mantém uma representação interna dos documentos. Edições manuais não percebidas levam a "correções" que revertem mudanças legítimas.

---

## 9. Gestão de Contexto

### 9.1 Estratégia de Delegação

O orquestrador coordena, subagentes implementam. Isso:

- Evita acúmulo de contexto no agente principal
- Permite paralelismo real
- Mantém o orquestrador ágil para decisões de alto nível

### 9.2 Trade-off de Tokens

Cada subagente re-lê os documentos de referência. Para mitigar:

- Agrupar tasks em subagentes grandes (menos re-leitura)
- Colar texto relevante no prompt ao invés de mandar ler o plano inteiro
- O `discovery.md` é essencial — evita que cada subagente re-explore o codebase

### 9.3 Quando Trocar de Sessão

Trocar de sessão quando o contexto atingir ~80% de uso:

- O log da sessão é salvo automaticamente em `~/.claude/projects/`
- Os documentos de referência contêm todo o contexto necessário para retomar
- Nova sessão começa com prompt apontando para os documentos relevantes

---

## 10. Ferramentas

| Ferramenta                  | Uso                                                                                                         |
| --------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Vitest**                  | Testes unitários (`yarn ng test`)                                                                           |
| **Playwright**              | Testes E2E (`npx playwright test`)                                                                          |
| **Playwright MCP**          | Validação visual (screenshots, computed styles)                                                             |
| **SonarQube MCP**           | Análise de qualidade de código via `mcp__sonarqube__analyze_code_snippet` (requer Docker)                   |
| **sonarqube-cli (`sonar`)** | CLI local — `sonar verify` requer SonarQube Cloud (não funciona com on-premise), usar MCP preferencialmente |
| **ESLint**                  | Linting (`yarn lint`)                                                                                       |
| **TypeScript**              | Typecheck (`npx tsc --noEmit`)                                                                              |
| **Express mock server**     | Dados mockados para desenvolvimento local                                                                   |
| **Azure DevOps MCP**        | Criação/leitura/atualização de work items (ferramentas `mcp__azure-devops__wit_*`)                          |
| **7pace API**               | Sincronização de horas via `scripts/sync-7pace.sh` (ou wrapper opcional `sync.sh`)               |

---

## 11. Checklist por Fase

Antes de prosseguir para a próxima fase, verificar:

- [ ] Subagente implementador concluiu e commitou
- [ ] Code review despachado e executado (lint + typecheck + SonarQube + testes + correções)
- [ ] Issues que precisam de decisão do usuário resolvidos
- [ ] Diário de implementação atualizado (com start time, end time e duração)
- [ ] Board sincronizado via Azure MCP (work item + tasks)
- [ ] Horas registradas no 7pace via `sync-7pace.sh`
- [ ] Testes unitários passando (todos, não só os novos)
- [ ] Testes E2E passando (quando aplicável)
- [ ] Push para o remote

---

## 12. Referências Cruzadas

- **Processo de criação de work items:** `docs/processo-work-items.md` + skill `processes/create-work-item.md`
- **Discovery do codebase:** `docs/discovery.md` + `templates/project-reference.template.md`
- **Convenções de testes E2E:** `docs/e2e.md`
- **Skills disponíveis:** `processes/` (start-workflow, create-work-item, phase-code-review, setup-*, timesync, spec-builder)
