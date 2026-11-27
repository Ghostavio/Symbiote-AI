---
name: timesync
description: "Use quando o usuário precisar registrar horas em uma ou mais ferramentas de controle de tempo configuradas no projeto — seja para o dia atual ou para múltiplos dias passados."
---

# Timesync — Sincronização de Horas em Ferramentas de Controle de Tempo

Registra horas de trabalho em **uma ou mais** ferramentas de controle de tempo configuradas no projeto (ex.: **7pace Timetracker**, **Clockify**, **Toggl Track**, **Harvest**), seguindo regras operacionais descobertas empiricamente para evitar relatórios distorcidos.

---

## Provedores: adaptadores prontos, exemplos e candidatos

Leia os provedores configurados no projeto antes de sincronizar — um projeto pode usar **exatamente um** provedor ou **vários simultaneamente** (ex.: ferramenta interna do cliente + ferramenta da consultoria).

| Provedor | Status no kit | Adaptador / referência | Instruções específicas do provedor |
| --- | --- | --- | --- |
| **7pace Timetracker** | **Pronto (enviado no kit)** | `scripts/sync-7pace.sh` | [`processes/setup-7pace.md`](setup-7pace.md) e [`scripts/README.md`](../scripts/README.md) |
| **Clockify** | **Pronto (enviado no kit)** | `.claude/integrations/timetracking/sync-clockify.sh` | [`.claude/integrations/timetracking/README.md`](../.claude/integrations/timetracking/README.md) |
| **7pace + Clockify (duplo)** | **Pronto (enviado no kit)** | `.claude/integrations/timetracking/sync.sh` | [`.claude/integrations/timetracking/README.md`](../.claude/integrations/timetracking/README.md) |
| **Toggl Track** | **Exemplo documentado** | Molde em `GUIA-DE-EXPANSAO.md` (Receita B) | [`GUIA-DE-EXPANSAO.md`](../GUIA-DE-EXPANSAO.md) e [`processes/integrar.md`](integrar.md) |
| **Harvest** | **Exemplo documentado** | Molde em `GUIA-DE-EXPANSAO.md` (Receita B) | [`GUIA-DE-EXPANSAO.md`](../GUIA-DE-EXPANSAO.md) e [`processes/integrar.md`](integrar.md) |
| **Tempo Timesheets for Jira** | **Candidato (não implementado)** | [Atlassian Marketplace — Tempo Timesheets](https://marketplace.atlassian.com/apps/6572/timesheets-by-tempo-jira-time-tracking?hosting=cloud&tab=overview) | Listado como adaptador candidato para times Jira até o kit implementar e verificar a integração |

### Como adicionar outro provedor

1. Crie um adaptador executável (ex.: `scripts/sync-<provedor>.sh`) seguindo o contrato comum do kit:
   - Flags: `--description`, `--start` (ISO 8601), `--end` (ISO 8601), `[--work-item-id]`, `[--activity-type]`, `[--dry-run]`.
   - Credenciais lidas **apenas** de variáveis de ambiente / secret manager (nunca hardcoded ou coladas no chat).
   - Retornar código de saída diferente de zero em qualquer erro HTTP ou de validação, e suportar `--dry-run` sem enviar requisições.
2. Documente setup, variáveis de ambiente e regras específicas (ex.: fuso horário, formato de descrição, IDs obrigatórios) num documento próprio do provedor.
3. Se o time sincroniza em **mais de um provedor**, componha os adaptadores num wrapper (como `.claude/integrations/timetracking/sync.sh`) — ver [`GUIA-DE-EXPANSAO.md`](../GUIA-DE-EXPANSAO.md) (Receita B) e [`processes/integrar.md`](integrar.md).

---

## Passo 0 — Identificar provedores configurados e container de "Outras Atividades"

Antes de qualquer sincronização:

1. **Descobrir provedores ativos no projeto:** consulte a memória/contexto da ferramenta de IA, a configuração do projeto e os scripts/env vars configurados para identificar **qual(is)** ferramenta(s) de controle de tempo estão ativas (um único provedor ou múltiplos). Confirme com o usuário se houver dúvida.
2. **Work item container (quando algum provedor vincula horas ao tracker):** Daily Scrum, reuniões e atividades sem User Story específica precisam ser lançadas num work item container ("Outras Atividades" ou equivalente). Esse ID varia por equipe/projeto e **não** é hardcoded nesta skill:
   - Consulte o mecanismo de memória/contexto da ferramenta de IA (`AGENTS.md`, auto-memory, `.cursor/rules/`, etc.) por um `<DAILY_WI>` já registrado e confirme com o usuário.
   - Se não houver registro, pergunte qual é o ID do container e ofereça salvá-lo para futuras sessões.

---

## Regras gerais (independentes de provedor)

### 1. Jornada padrão do time (exemplo: 8h/dia útil)

Alinhe o total diário à jornada do time. Exemplo comum: **8h por dia útil** (`7h 45min` produtivos + `15min` de Daily Scrum em `<DAILY_WI>`). Ajuste se o projeto tiver outra política.

### 2. Sessões individuais, nunca consolidadas

**NUNCA** crie uma única entrada "consolidada" somando vários dias em um único registro:
- Uma entrada com `start` único e duração acumulada (ex.: 31h) é alocada integralmente ao primeiro dia na maioria das ferramentas, distorcendo relatórios diários.
- **Sempre** registre **uma entrada por sessão** conforme a tabela de sessões / diário de implementação.

### 3. Convenção de descrição por provedor

Respeite como cada provedor representa vínculo com o tracker:
- **Provedores com vínculo nativo a work item** (ex.: 7pace, Tempo/Jira): use apenas o nome da atividade, **sem prefixo `{ID}:`** (ex.: `Setup e Infraestrutura`).
- **Provedores sem vínculo nativo ao tracker** (ex.: Clockify, Toggl, Harvest): inclua o prefixo `{WorkItemId}: ` quando houver item vinculado (ex.: `1234: Setup e Infraestrutura`), exceto atividades genéricas como `Daily`.
- **Daily:** use exatamente `Daily` (sem "Scrum" e sem prefixo de work item).

### 4. Fuso horário consistente

`--start` e `--end` são timestamps ISO 8601 com fuso explícito. `Z` significa UTC; para indicar horário local, use o offset válido naquela data (por exemplo, `-03:00`). Os scripts calculam a duração pelo instante representado e enviam os mesmos timestamps aos provedores, sem inferir o fuso do computador nem aplicar conversões fixas. Em regiões com horário de verão, informe o offset vigente na data da sessão.

### 5. Segredos fora do contexto da IA

Nunca peça nem cole tokens no chat. Use variáveis de ambiente carregadas via Keychain / 1Password / Bitwarden / arquivo local ignorado pelo git (ver instruções de setup de cada provedor).

---

## Fluxo

### Passo 1 — Ter a fonte de verdade

A lista de sessões deve vir do diário de implementação ou de uma tabela consolidada de sessões do projeto:

| Data | Start Time | End Time | Duração | WI | Activity Type |
| --- | --- | --- | --- | --- | --- |
| 2026-01-14 | 14:00 | 16:00 | 2h 00min | #1235 | Desenvolvimento |

Confira se cada dia útil fecha na jornada esperada (descontando intervalos como almoço).

### Passo 2 — Sincronizar nos provedores configurados

Execute o adaptador correspondente aos provedores ativos do projeto (rode `--dry-run` antes quando testar uma configuração nova):

**Exemplo — 1 provedor (7pace):**
```bash
scripts/sync-7pace.sh \
  --description "Setup e Infraestrutura" \
  --start "2026-01-14T10:00:00-03:00" \
  --end "2026-01-14T10:30:00-03:00" \
  --work-item-id 1234 \
  --activity-type "Desenvolvimento"
```

**Exemplo — 1 provedor (Clockify):**
```bash
.claude/integrations/timetracking/sync-clockify.sh \
  --description "1234: Setup e Infraestrutura" \
  --start "2026-01-14T10:00:00-03:00" \
  --end "2026-01-14T10:30:00-03:00"
```

**Exemplo — múltiplos provedores (wrapper 7pace + Clockify):**
```bash
.claude/integrations/timetracking/sync.sh \
  --description "Setup e Infraestrutura" \
  --start "2026-01-14T10:00:00-03:00" \
  --end "2026-01-14T10:30:00-03:00" \
  --work-item-id 1234 \
  --activity-type "Desenvolvimento"
```

> Para lotes grandes, prefira um script de lote dedicado para a API do provedor (com dry-run e conferência de status HTTP) em vez de disparar dezenas de chamadas manuais sem verificação.
> Se uma sincronização multi-provedor falhar parcialmente, **não reexecute o provedor que já teve sucesso** — reenvie apenas o provedor que falhou usando o script específico dele. Se um **timeout** ou erro de rede deixar o resultado de uma gravação incerto, **consulte e reconcilie os lançamentos existentes no provedor antes de tentar novamente**, para evitar duplicar uma entrada que já foi gravada com sucesso.

### Passo 3 — Validar distribuição diária

Após sincronizar, confira em cada provedor configurado se os dias úteis fecham no total esperado:

```text
Daily (09:30-09:45)             15min
Produtivo manhã (09:00-09:30)    0h 30min
Produtivo manhã (09:45-12:00)    2h 15min
Produtivo tarde (13:00-18:00)    5h 00min
                               ─────────
                                 8h 00min ✓
```

Se algum dia ultrapassar a jornada esperada, **não assuma automaticamente que houve entrada consolidada** — horas extras legítimas ou lançamentos sobrepostos também podem explicar o total. Inspecione os lançamentos existentes no provedor, confirme com o usuário qual registro (se algum) está incorreto e **obtenha aprovação explícita antes de deletar ou recriar qualquer lançamento**.

---

## Anti-padrões

- **Entrada consolidada multi-dia:** nunca agrupe vários dias em um único lançamento.
- **Misturar convenções entre provedores:** não envie prefixo `{ID}:` em provedores que já vinculam `workItemId` nativamente, nem omita `{ID}:` quando o provedor depende do texto para rastreabilidade.
- **Usar `"Daily Scrum"` em vez de `"Daily"`** ou prefixar Daily com ID de work item.
- **Ignorar falha silenciosa ou duplicar lançamento em falha parcial:** sempre confira o exit code de cada adaptador antes de tentar novamente.

---

## Checklist de sincronização

Antes de considerar concluído:

- [ ] Todos os provedores configurados no projeto foram sincronizados (1 ou N)
- [ ] Cada dia útil fecha na jornada configurada do time (ex.: 8h)
- [ ] Nenhuma entrada consolidada ultrapassa um dia
- [ ] Convenções de descrição, fuso horário e projeto/activity type de cada provedor foram respeitadas
- [ ] Todos os work items referenciados existem no tracker (quando aplicável)

---

## Referências específicas por provedor

- **7pace Timetracker:** [`processes/setup-7pace.md`](setup-7pace.md) · [`scripts/README.md`](../scripts/README.md) · `scripts/sync-7pace.sh`
- **Clockify e wrapper multi-provedor:** [`.claude/integrations/timetracking/README.md`](../.claude/integrations/timetracking/README.md)
- **Adicionar novos provedores (Toggl Track, Harvest, Tempo Timesheets for Jira, etc.):** [`GUIA-DE-EXPANSAO.md`](../GUIA-DE-EXPANSAO.md) (Receita B) · [`processes/integrar.md`](integrar.md)
