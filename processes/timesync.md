---
name: timesync
description: "Use quando o usuário precisar sincronizar horas de trabalho com o 7pace Timetracker — tanto para o dia atual quanto para múltiplos dias passados."
---

# Timesync — Sincronização com 7pace Timetracker

Registra horas de trabalho no 7pace Timetracker seguindo regras descobertas empiricamente para evitar relatórios distorcidos.

## Passo 0 — Identificar o WI de "Outras Atividades"

Daily Scrum, reuniões e atividades sem User Story específica precisam ser lançadas em um **work item container** (genericamente chamado "Outras Atividades" ou similar). Esse ID **varia por equipe/projeto** e não é hardcoded nesta skill.

Antes de qualquer sincronização que envolva Daily ou reuniões:

1. Consultar o mecanismo de memória/contexto da ferramenta de AI em uso (auto-memory do Claude Code, `AGENTS.md`, `.cursor/rules/<context>.mdc` com `alwaysApply: true`, etc.) para verificar se o usuário tem um **Daily WI** já registrado.
2. Se encontrar, usar esse ID e confirmar com o usuário (ex: "Vou usar o WI [ID] como Daily — confirma?").
3. Se não encontrar, perguntar:

   > Qual é o ID do work item que você usa como container de "Outras Atividades" no Azure DevOps Board (Daily, reuniões, atividades sem US específica)?

4. Após receber o ID, oferecer salvá-lo no mecanismo de memória da ferramenta para reuso em futuras sessões.

A partir daqui, este documento se refere a esse ID como `<DAILY_WI>`.

## Regras críticas

### 1. Jornada padrão — sempre 8 horas por dia

Cada dia útil deve totalizar **exatamente 8h** de registros:
- **7h 45min** de trabalho produtivo
- **15 min** de Daily Scrum (`<DAILY_WI>`, Activity Type "Rituais Scrum")

### 2. Sessões individuais, nunca consolidadas

**NUNCA** crie uma única entrada "consolidada" por work item somando todo o tempo. Isso quebra a distribuição diária porque:
- A entrada usa um `timestamp` único + `length` total
- O 7pace aloca tudo ao dia do `timestamp`
- Um WI com 31h começando em 12/01 gera "31h no dia 12" ao invés de distribuir

**Sempre** registre **uma entrada por sessão** conforme o timetracking consolidado (tabela de sessões em algum doc do projeto).

### 3. Formato de descrição

Descrição é apenas o nome da atividade, **sem prefixo `{ID}:`** — o `workItemId` já está nativamente vinculado ao worklog no 7pace.

```
✅ Correto:   Setup e Infraestrutura
❌ Errado:    1234: Setup e Infraestrutura
```

**Daily:** descrição exata é `Daily` (não "Daily Scrum").

### 4. Activity Types no 7pace

Os GUIDs de Activity Type são específicos do tenant do 7pace. Substitua os marcadores abaixo pelos GUIDs do seu tenant, consultando a configuração via API ou UI do 7pace.

| Nome              | GUID                                   | Uso                                |
| ----------------- | -------------------------------------- | ---------------------------------- |
| `Desenvolvimento` | `<7PACE_ACTIVITY_ID_DESENVOLVIMENTO>`  | Implementação de código            |
| `Operação`        | `<7PACE_ACTIVITY_ID_OPERACAO>`         | Docs, config, evidências           |
| `Reunião`         | `<7PACE_ACTIVITY_ID_REUNIAO>`          | Reuniões                           |
| `Rituais Scrum`   | `<7PACE_ACTIVITY_ID_RITUAIS_SCRUM>`    | Daily, planning, review            |
| `Planejamento`    | `<7PACE_ACTIVITY_ID_PLANEJAMENTO>`     | Planejamento de tarefas            |
| `Homologação`     | `<7PACE_ACTIVITY_ID_HOMOLOGACAO>`      | Testes e validação                 |
| `Treinamento`     | `<7PACE_ACTIVITY_ID_TREINAMENTO>`      | Capacitação                        |

### 5. Timezone — sempre BRT

O 7pace usa `timestamp` em UTC (`Z`) + campo `timeZone: -180` para conversão. O script `sync-7pace.sh` já aplica isso automaticamente.

### 6. WorkItem de "Outras Atividades"

`<DAILY_WI>` (consultado/perguntado no Passo 0) é o container genérico para:
- Daily Scrum (Activity Type: Rituais Scrum)
- Reuniões (Activity Type: Reunião)
- Qualquer atividade que não se encaixa em uma User Story específica

## Fluxo

### Passo 1 — Ter a fonte de verdade

A lista de sessões deve vir de um timetracking consolidado (ex: tabela "Tabela completa de sessões" em algum doc de scrum do projeto). Formato esperado de cada linha:

| Data       | Start Time | End Time | Duração  | WI      | Activity Type   |
| ---------- | ---------- | -------- | -------- | ------- | --------------- |
| 2026-01-14 | 14:00      | 16:00    | 2h 00min | #1235   | Desenvolvimento |

Cada dia deve totalizar 8h contando:
- Dailies (09:30-09:45, 15min)
- Sessões produtivas (outras linhas)
- Almoço 12:00-13:00 NÃO conta

### Passo 2 — Sincronizar

Use o script compartilhado:

```bash
scripts/sync-7pace.sh \
  --description "Setup e Infraestrutura" \
  --start "2026-01-14T10:00:00Z" \
  --end "2026-01-14T10:30:00Z" \
  --work-item-id 1234 \
  --activity-type "Desenvolvimento"
```

Para lotes grandes, use um script Python com HTTP direto (ver exemplo abaixo) ao invés de invocar o shell N vezes.

### Passo 3 — Validar distribuição diária

Após sincronizar, verificar no 7pace que cada dia soma 8h:

```
Daily (09:30-09:45)             15min
Produtivo manhã (9-9:30)         0h 30min
Produtivo manhã (09:45-12:00)    2h 15min
Produtivo tarde (13:00-18:00)    5h 00min
                               ─────────
                                 8h 00min ✓
```

Se um dia tem mais que 8h (ex: 31h), significa que uma entrada foi criada como "consolidada" — deletar e refazer com sessões individuais.

## Anti-padrões

### ❌ Entrada consolidada por work item
```
# ERRADO — 31h alocadas em um único dia
sync-7pace.sh --start "2026-01-12T09:00Z" --end "2026-01-13T16:00Z" \
  --description "consolidado" --work-item-id 1236
```

### ❌ Prefixo {ID}: na descrição
```
# ERRADO — o workItemId já está no vínculo
comment: "1234: Setup e Infraestrutura"

# CORRETO
comment: "Setup e Infraestrutura"
```

### ❌ "Daily Scrum" ao invés de "Daily"
```
# ERRADO
description: "Daily Scrum"

# CORRETO
description: "Daily"
```

## Script Python para sincronização em lote

Quando registrar muitas sessões, usar Python com requests HTTP diretos é mais eficiente que invocar `sync-7pace.sh` em loop. Estrutura básica (substitua `<DAILY_WI>` pelo ID confirmado no Passo 0):

```python
import os, json, urllib.request

# Pré-requisito: SEVENPACE_API_TOKEN e SEVENPACE_BASE_URL exportados
# (ver setup-7pace para configuração via Keychain/1Password/etc)
TOKEN = os.environ['SEVENPACE_API_TOKEN']
BASE = os.environ['SEVENPACE_BASE_URL']

ACT_DESENV = "<7PACE_ACTIVITY_ID_DESENVOLVIMENTO>"
ACT_OPER = "<7PACE_ACTIVITY_ID_OPERACAO>"
ACT_RITUAIS = "<7PACE_ACTIVITY_ID_RITUAIS_SCRUM>"
ACT_REUNIAO = "<7PACE_ACTIVITY_ID_REUNIAO>"

DAILY_WI = <DAILY_WI>  # ID confirmado no Passo 0

def http(method, url, headers, body=None):
    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read().decode('utf-8')

def duration_seconds(start_hhmm, end_hhmm):
    """Diferença em segundos entre dois horários no formato 'HH:MM'."""
    sh, sm = map(int, start_hhmm.split(':'))
    eh, em = map(int, end_hhmm.split(':'))
    return (eh * 3600 + em * 60) - (sh * 3600 + sm * 60)

# Lista de sessões (data, start, end, wi_id, activity_id, nome)
SESSIONS = [
    ('2026-01-14', '10:00', '10:30', 1234, ACT_DESENV, 'Setup e Infraestrutura'),
    # ...
]

for date, st, en, wi_id, act_id, name in SESSIONS:
    length = duration_seconds(st, en)
    body = {
        'workItemId': wi_id,
        'length': length,
        'timestamp': f"{date}T{st}:00Z",
        'comment': name,
        'activityTypeId': act_id,
        'timeZone': -180,
    }
    http('POST', f"{BASE}/api/rest/workLogs?api-version=3.2",
         {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'},
         body)
```

## Checklist de sincronização

Antes de considerar concluído:

- [ ] Cada dia útil totaliza exatamente 8h no 7pace
- [ ] Cada dia tem uma entrada de Daily de 15min (`<DAILY_WI>`, Activity Type "Rituais Scrum")
- [ ] Descrições não têm prefixo `{ID}:`
- [ ] Nenhuma entrada "consolidada" que ultrapasse um dia
- [ ] Todos os worklogs têm `workItemId` válido no Azure DevOps

## Referências

- **Script:** `scripts/sync-7pace.sh`
- **Setup 7pace:** `/setup-7pace` skill
- **Env vars (preferido):** `SEVENPACE_API_TOKEN`, `SEVENPACE_BASE_URL` (configurar via skill `/setup-7pace`)
