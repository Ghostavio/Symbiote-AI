# Scripts — Timetracking (7pace)

## sync-7pace.sh

Registra entradas de tempo no [7pace Timetracker](https://www.7pace.com/) via REST API v3.2, integrado ao Azure DevOps Board.

O helper `time-entry-interval.py`, usado pelos adaptadores 7pace e Clockify, valida timestamps com fuso explícito e calcula o tempo decorrido sem depender do timezone do sistema operacional.

### Configuração rápida (via skill)

Se você usa uma ferramenta de AI compatível, invoque a skill **`/setup-7pace`** — ela guia todo o processo escolhendo onde armazenar o token (macOS Keychain, 1Password, Bitwarden ou shell config), de forma que **o token nunca passa pelo contexto do AI**.

### Configuração manual

1. **Obter token do 7pace:** Settings > Reporting and API > Create New Token

2. **Configurar env vars** (recomendado: via secret manager para encryption-at-rest):

   **Opção A — macOS Keychain** (recomendado para Mac):
   ```bash
   # Salvar (vai pedir o token interativamente — silent input)
   security add-generic-password -s '7pace-api-token' -a "$USER" -w
   # No ~/.zshrc:
   export SEVENPACE_API_TOKEN=$(security find-generic-password -s '7pace-api-token' -w 2>/dev/null)
   export SEVENPACE_BASE_URL='https://<SEVENPACE_ORG>.timehub.7pace.com'
   ```

   **Opção B — 1Password / Bitwarden**: armazenar o token e exportar via `op read` / `bw get` no `~/.zshrc`.

   **Opção C — Direto em `~/.zshrc`** (token plain-text num arquivo seu):
   ```bash
   export SEVENPACE_API_TOKEN='seu-token'
   export SEVENPACE_BASE_URL='https://<SEVENPACE_ORG>.timehub.7pace.com'
   ```

   **Opção D — `.env` legado** (deprecado, mantido pra retrocompat):
   `.claude/integrations/timetracking/.env` ainda funciona como fallback, mas migrar para env vars exportados é recomendado.

3. **Recarregar shell:** `source ~/.zshrc` (ou abra novo terminal)

### Uso

```bash
# Registrar tempo em um work item
./scripts/sync-7pace.sh \
  --description "FASE 1: Camada de domínio" \
  --start "2026-01-14T14:00:00-03:00" \
  --end "2026-01-14T16:00:00-03:00" \
  --work-item-id 1234 \
  --activity-type "Desenvolvimento"

# Dry run (mostra o que seria enviado, sem criar)
./scripts/sync-7pace.sh \
  --description "FASE 1: Camada de domínio" \
  --start "2026-01-14T14:00:00-03:00" \
  --end "2026-01-14T16:00:00-03:00" \
  --work-item-id 1234 \
  --dry-run
```

### Parâmetros

| Parâmetro         | Obrigatório | Descrição                                                   |
| ----------------- | ----------- | ----------------------------------------------------------- |
| `--description`   | Sim         | Descrição da atividade                                      |
| `--start`         | Sim         | Início ISO 8601 com fuso explícito (ex: `2026-01-14T14:00:00-03:00`) |
| `--end`           | Sim         | Fim ISO 8601 com fuso explícito                             |
| `--work-item-id`  | Sim         | ID do work item no Azure DevOps                             |
| `--activity-type` | Não         | Tipo de atividade (default: `Desenvolvimento`)              |
| `--dry-run`       | Não         | Mostra o JSON sem carregar credenciais nem chamar a API    |

### Activity Types disponíveis

| Nome              | Descrição                              |
| ----------------- | -------------------------------------- |
| `Desenvolvimento` | Implementação de código (default)      |
| `Operação`        | Documentação, configuração, evidências |
| `Reunião`         | Reuniões                               |
| `Rituais Scrum`   | Daily, planning, review, retro         |
| `Planejamento`    | Planejamento de tarefas                |
| `Homologação`     | Testes e validação                     |
| `Treinamento`     | Capacitação                            |

### Integração com workflow AI

Este script é chamado automaticamente pelo orquestrador durante o workflow de implementação (seções 4.4 e 5.5 do `docs/workflow.md`):

1. Antes de despachar subagente → registra start time no diário
2. Após entrega + code review → consulta `git log -1 --format=%aI` para end time ISO 8601 com offset
3. Chama `sync-7pace.sh` com os timestamps para registrar no 7pace

