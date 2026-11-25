---
name: timesync-clockify
description: "Use quando o usuário precisar registrar as mesmas horas também no Clockify, além do 7pace Timetracker."
model: opus
---

# Timesync Clockify — Extensão opcional para o Clockify

Skill opcional que complementa a skill `timesync` com as regras do Clockify, para quem precisa registrar as mesmas horas nas duas plataformas (por exemplo, uma consultoria que cobra por hora).

**Pré-requisito:** A skill `timesync` do repositório deve ter sido lida primeiro — ela define as regras gerais (8h/dia, sessões individuais, WI de "Outras Atividades" `<DAILY_WI>`, Activity Types).

## Regras específicas do Clockify

### 1. Prefixo `{WorkItemId}:` na descrição

Diferente do 7pace (que tem o workItemId no vínculo nativo), o Clockify não tem referência ao Azure DevOps. A descrição deve carregar esse contexto:

| Plataforma | Formato | Exemplo |
|-----------|---------|---------|
| **7pace** | Apenas o nome (sem prefixo) | `Setup e Infraestrutura` |
| **Clockify** | `{WorkItemId}: {nome}` | `1234: Setup e Infraestrutura` |

**Exceção Daily:** em ambas as plataformas, a Daily é apenas `Daily` (sem prefixo, sem "Scrum"). A Daily é genérica o suficiente que não precisa do ID.

### 2. Timezone — BRT explícito (-03:00)

O Clockify **não entende `Z` como intenção local**. Enviar com offset BRT explícito:

```
❌ Errado:   2026-01-14T09:00:00Z      (interpretado como UTC, vira 06:00 BRT)
✅ Correto:  2026-01-14T09:00:00-03:00 (BRT explícito)
```

### 3. ProjectId obrigatório

Todas as entradas do projeto vão para um projeto fixo no Clockify (ex.: `Projeto Exemplo`). O ID fica em `.env` (`CLOCKIFY_PROJECT_ID`).

## Script de sincronização

O wrapper opcional `.claude/integrations/timetracking/sync.sh` chama ambas as plataformas na sequência correta:

```bash
.claude/integrations/timetracking/sync.sh \
  --description "Setup e Infraestrutura" \
  --start "2026-01-14T10:00:00Z" \
  --end "2026-01-14T10:30:00Z" \
  --work-item-id 1234 \
  --activity-type "Desenvolvimento"
```

Internamente:
1. Chama `scripts/sync-7pace.sh` (sem prefixo)
2. Chama `.claude/integrations/timetracking/sync-clockify.sh` (com prefixo `1234: `)

## Ajuste em massa de descrições existentes

Se entradas foram criadas sem prefixo no Clockify, usar Python script para adicionar:

```python
import re
PREFIX_RE = re.compile(r'^\d+:\s*')

NAME_TO_WI = {
    "Setup e Infraestrutura": 1234,
    "Camada de Domínio": 1235,
    # ... mapeamento nome → work item ID
    "Reunião de alinhamento": 1236,
}

for entry in clockify_entries:
    old = entry['description'].strip()
    core = PREFIX_RE.sub('', old)  # remover prefixo existente
    if core == 'Daily Scrum':
        core = 'Daily'

    if core == 'Daily':
        new = 'Daily'  # sem prefixo
    else:
        wi_id = NAME_TO_WI.get(core)
        new = f"{wi_id}: {core}" if wi_id else core

    # PUT com nova description
```

## API Clockify — endpoints essenciais

- **Base:** `https://api.clockify.me/api/v1`
- **Auth:** header `X-Api-Key: {token}`
- **Criar entrada:** `POST /workspaces/{workspaceId}/time-entries`
- **Listar:** `GET /workspaces/{workspaceId}/user/{userId}/time-entries?start=...&end=...`
- **Atualizar:** `PUT /workspaces/{workspaceId}/time-entries/{id}`
- **Deletar:** `DELETE /workspaces/{workspaceId}/time-entries/{id}`

Body para criar:
```json
{
  "start": "2026-01-14T10:00:00-03:00",
  "end": "2026-01-14T10:30:00-03:00",
  "description": "1234: Setup e Infraestrutura",
  "billable": true,
  "projectId": "<CLOCKIFY_PROJECT_ID>"
}
```

## Credenciais (arquivo `.env`)

Em `.claude/integrations/timetracking/.env`:
```bash
CLOCKIFY_API_TOKEN=...
CLOCKIFY_WORKSPACE_ID=<CLOCKIFY_WORKSPACE_ID>
CLOCKIFY_USER_ID=...
CLOCKIFY_PROJECT_ID=<CLOCKIFY_PROJECT_ID>
```

Para setup inicial: ver `/setup-7pace` do repo (que cobre 7pace) + configurar manualmente as variáveis Clockify acima.

## Anti-padrões (Clockify-específicos)

### ❌ Sem prefixo `{ID}:` (exceto Daily)
```
# ERRADO — sem contexto de work item
description: "Setup e Infraestrutura"

# CORRETO
description: "1234: Setup e Infraestrutura"
```

### ❌ Prefixo em Daily
```
# ERRADO — Daily é genérica, sem prefixo
description: "1236: Daily"

# CORRETO
description: "Daily"
```

### ❌ Timestamp em UTC (Z)
```
# ERRADO — 09:00Z vira 06:00 BRT no Clockify
start: "2026-01-14T09:00:00Z"

# CORRETO
start: "2026-01-14T09:00:00-03:00"
```

## Checklist extra (além da skill timesync principal)

- [ ] Cada entrada Clockify tem prefixo `{WorkItemId}: ` (exceto Daily)
- [ ] Timestamps usam offset `-03:00`, nunca `Z`
- [ ] `projectId` correto em todas as entradas
- [ ] Dailies estão sem prefixo, apenas `Daily`

## Referências

- **Wrapper opcional:** `.claude/integrations/timetracking/sync.sh`
- **Script Clockify:** `.claude/integrations/timetracking/sync-clockify.sh`
- **Env:** `.claude/integrations/timetracking/.env` (modelo em `.env.example`, na mesma pasta)
- **Clockify MCP:** `.claude/integrations/clockify-mcp/` (opcional; a pasta é criada pelo clone descrito em `.claude/integrations/timetracking/README.md`)
- **Skill base:** `timesync` (compartilhada, em `processes/`)
