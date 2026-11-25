---
name: setup-7pace
description: "Use quando a integração com 7pace Timetracker não estiver configurada no ambiente, ou quando o script `sync-7pace.sh` falhar por falta de token."
---

# Setup 7pace Timetracker

Configura o token do 7pace como variável de ambiente, mantendo o token **fora do contexto do AI**. O script `scripts/sync-7pace.sh` lê o token diretamente do env var, sem nunca passar pelo agente.

## ⚠️ Regra crítica de segurança

**O usuário NUNCA deve colar o token na conversa com o AI.** Toda manipulação do token acontece no terminal do usuário. A AI orienta os passos, mas o valor do token só transita entre o usuário, o terminal e o destino final (Keychain, secret manager ou shell config).

Se em qualquer momento o usuário oferecer colar o token na conversa, **recusar** e redirecioná-lo a fazer no próprio terminal seguindo os passos abaixo.

## Passo 1 — Gerar token

Apresentar ao usuário:

> Você precisa gerar um token de API no 7pace.
>
> 1. Acesse: https://<AZURE_ORG>.visualstudio.com/<AZURE_PROJECT>/_apps/hub/7pace.Timetracker.Configuration#apiSettings
> 2. Clique em **Create New Token**
> 3. Copie o token (mantenha aberto na clipboard temporariamente — você vai colá-lo no seu terminal no próximo passo, **não nesta conversa**)

## Passo 2 — Escolher onde armazenar

Perguntar ao usuário:

> Onde você quer armazenar o token? Numere a opção:
>
> 1. **macOS Keychain** — encrypted at rest, integrado ao OS (recomendado para macOS)
> 2. **1Password CLI (`op`)** — se você já tem conta 1Password
> 3. **Bitwarden CLI (`bw`)** — alternativa gratuita open-source
> 4. **Script de configuração** — armazena o token em `~/.7pace` e dá `source` dele no `~/.zshrc`/`~/.bashrc`. Mais robusto que colocar o token direto no rc: se você abrir o rc em uma IDE com AI, a chave não é exposta porque vive num arquivo separado que você nunca abre.
> 5. **Outro secret manager** — me diga qual e eu te oriento

Aguardar a resposta antes de prosseguir. Para o passo 3, seguir apenas a opção escolhida.

## Passo 3 — Configurar conforme escolha

### Opção 1: macOS Keychain

Apresentar ao usuário (para o usuário rodar no terminal dele):

> Cole estes comandos um a um no seu terminal. O primeiro vai pedir o token interativamente — cole quando solicitado:
>
> ```bash
> # Armazenar token no Keychain (-w sem valor faz prompt interativo silencioso)
> security add-generic-password -s '7pace-api-token' -a "$USER" -w
> ```
>
> Em seguida, edite seu `~/.zshrc` (ou `~/.bashrc` se usar bash) e adicione:
>
> ```bash
> # 7pace Timetracker — token via macOS Keychain
> export SEVENPACE_API_TOKEN=$(security find-generic-password -s '7pace-api-token' -w 2>/dev/null)
> export SEVENPACE_BASE_URL='https://<SEVENPACE_ORG>.timehub.7pace.com'
> ```
>
> Recarregue o shell:
>
> ```bash
> source ~/.zshrc
> ```

### Opção 2: 1Password CLI (`op`)

Apresentar ao usuário:

> Cole no seu terminal:
>
> ```bash
> # Verificar que op está autenticado
> op whoami || op signin
>
> # Criar item (vai pedir o valor interativamente — escolha "API Credential" e cole o token)
> op item create --category='API Credential' --title='7pace Timetracker' \
>   --vault='Personal' \
>   credential='[type-token-here]'
> ```
>
> Substitua `[type-token-here]` pelo token (cole no comando antes de executar). Se preferir não colar no comando, use `op item edit` depois.
>
> Edite seu `~/.zshrc` adicionando:
>
> ```bash
> # 7pace Timetracker — token via 1Password
> export SEVENPACE_API_TOKEN=$(op read 'op://Personal/7pace Timetracker/credential' 2>/dev/null)
> export SEVENPACE_BASE_URL='https://<SEVENPACE_ORG>.timehub.7pace.com'
> ```
>
> Recarregue: `source ~/.zshrc`

### Opção 3: Bitwarden CLI (`bw`)

Apresentar ao usuário:

> Cole no seu terminal:
>
> ```bash
> # Login + unlock se necessário
> bw login
> export BW_SESSION=$(bw unlock --raw)
>
> # Criar item de Secure Note (cole o token quando perguntado)
> bw send create --hidden --no-clipboard --text-from-input --name '7pace Timetracker'
> ```
>
> (alternativa mais simples: criar manualmente via UI do Bitwarden e usar o nome `7pace Timetracker`)
>
> Edite seu `~/.zshrc`:
>
> ```bash
> # 7pace Timetracker — token via Bitwarden
> export BW_SESSION=$(bw unlock --raw 2>/dev/null)  # ou armazenar em outra var
> export SEVENPACE_API_TOKEN=$(bw get notes '7pace Timetracker' 2>/dev/null)
> export SEVENPACE_BASE_URL='https://<SEVENPACE_ORG>.timehub.7pace.com'
> ```
>
> Recarregue: `source ~/.zshrc`

### Opção 4: Script de configuração

**macOS / Linux / WSL** (`scripts/setup-7pace.sh`):

> Rode no seu terminal (no diretório do repo):
>
> ```bash
> ./scripts/setup-7pace.sh
> ```
>
> O script vai:
> 1. Detectar seu OS e shell (zsh/bash) e o arquivo rc correto
> 2. **Em macOS**: oferecer escolha entre **(a) macOS Keychain** (recomendado,
>    encrypted at rest — `~/.7pace` contém apenas `security find-generic-password`,
>    não o token) ou **(b) arquivo plain-text em `~/.7pace`** (chmod 600).
>    **Em Linux/WSL**: usa direto o arquivo plain-text.
> 3. Pedir o token interativamente (input oculto, não fica no histórico)
> 4. Gravar conforme a escolha (Keychain ou `~/.7pace`)
> 5. Adicionar a linha `source ~/.7pace` no seu `~/.zshrc` ou `~/.bashrc`
>
> Depois do script, recarregue: `source ~/.zshrc` (ou abra novo terminal).

**Windows (PowerShell 5.1+ ou 7.x)** (`scripts/setup-7pace.ps1`):

> Rode no PowerShell (no diretório do repo):
>
> ```powershell
> .\scripts\setup-7pace.ps1
> ```
>
> Equivalente do `.sh`: pede o token via `Read-Host -AsSecureString` (input oculto),
> grava em `$HOME\.7pace.ps1` com ACL restrita ao seu usuário, e adiciona
> `. $HOME\.7pace.ps1` no `$PROFILE`. Recarregue com `. $PROFILE` ou novo terminal.
>
> Se você usa WSL ao invés do PowerShell nativo, rode o `.sh` dentro do WSL.

**Vantagem (em qualquer OS):** se você um dia abrir o `~/.zshrc`/`$PROFILE` em uma
IDE com AI, a chave não é exposta — vive num arquivo separado (`~/.7pace` ou
`$HOME\.7pace.ps1`) que você nunca abre. A IDE/AI lê apenas o rc/profile, não
navega recursivamente para arquivos `source`-ed.

### Opção 5: Outro secret manager

Pedir ao usuário para descrever qual ferramenta usa. O padrão geral:

1. Armazenar token na ferramenta (sem expor na conversa)
2. No `~/.zshrc`, exportar a env var lendo da ferramenta:
   ```bash
   export SEVENPACE_API_TOKEN=$(<comando-da-ferramenta>)
   export SEVENPACE_BASE_URL='https://<SEVENPACE_ORG>.timehub.7pace.com'
   ```

## Passo 4 — Validar configuração (sem revelar token)

Após o usuário confirmar que recarregou o shell, validar via Bash tool:

```bash
[[ -n "${SEVENPACE_API_TOKEN}" ]] && echo "✓ SEVENPACE_API_TOKEN está configurado" || echo "✗ SEVENPACE_API_TOKEN NÃO está visível"
[[ -n "${SEVENPACE_BASE_URL}" ]] && echo "✓ SEVENPACE_BASE_URL: $SEVENPACE_BASE_URL" || echo "✗ SEVENPACE_BASE_URL NÃO está visível"
```

> **Importante:** este comando só revela "set"/"not set", nunca o valor do token.

Se algum sair como "NÃO está visível":
- Para Keychain/1Password/Bitwarden: o comando de leitura pode estar falhando (verificar autenticação no secret manager)
- Para `~/.zshrc` direto: confirmar que o usuário recarregou o shell (`source ~/.zshrc`) ou abriu novo terminal
- Reiniciar a aplicação de AI também pode ser necessário (ela herda env vars do shell que a iniciou — se foi iniciada antes do export, não tem)

## Passo 5 — Testar conexão

Validar que o token funciona contra a API do 7pace:

```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" \
  -H "Authorization: Bearer $SEVENPACE_API_TOKEN" \
  "$SEVENPACE_BASE_URL/api/odata/v3.2/workLogsOnly?\$top=1"
```

Esperado: `HTTP 200`. Se 401: token inválido (regenerar). Se 403: permissões. Se outro: VPN ou conectividade.

> **Nota:** a variável `$SEVENPACE_API_TOKEN` aqui é expandida pelo shell antes do AI ver, então o AI ainda não vê o valor.

## Passo 6 — Teste end-to-end (criar + deletar worklog)

Para garantir que escrita funciona, criar uma entrada de teste e deletar em seguida.

Antes de rodar, identificar um **work item de teste** (`<TEST_WI>`):

1. Consultar o mecanismo de memória/contexto da ferramenta de AI por um WI de "Outras Atividades" / Daily container já registrado
2. Se não encontrar, perguntar ao usuário:
   > Qual ID de work item posso usar para criar uma entrada de teste (vou criar e deletar imediatamente, então não fica nenhum registro)?

```bash
# Substitua <TEST_WI> pelo ID identificado acima
# e <7PACE_ACTIVITY_ID_DESENVOLVIMENTO> pelo GUID do seu tenant (ver Activity Types abaixo)
TEST_WI=<TEST_WI>

# Criar (timestamp em UTC, length em segundos)
RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $SEVENPACE_API_TOKEN" \
  -H "Content-Type: application/json" \
  "$SEVENPACE_BASE_URL/api/rest/workLogs?api-version=3.2" \
  -d "{
    \"workItemId\": $TEST_WI,
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"length\": 60,
    \"activityTypeId\": \"<7PACE_ACTIVITY_ID_DESENVOLVIMENTO>\",
    \"comment\": \"TESTE AUTOMATICO - deletar\",
    \"timeZone\": -180
  }")
ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('id',''))")
echo "Worklog criado: $ID"

# Deletar
curl -s -o /dev/null -w "Delete HTTP %{http_code}\n" -X DELETE \
  -H "Authorization: Bearer $SEVENPACE_API_TOKEN" \
  "$SEVENPACE_BASE_URL/api/rest/workLogs/$ID?api-version=3.2"
```

Esperado: ID retornado + `Delete HTTP 200`.

## Passo 7 — Confirmar

Se tudo passou:

> Setup do 7pace concluído.
>
> **Onde está o token:** [escolha do usuário — Keychain / 1Password / Bitwarden / ~/.zshrc]
> **Env vars exportadas:** `SEVENPACE_API_TOKEN`, `SEVENPACE_BASE_URL`
> **AI nunca viu o valor do token.**
>
> Como usar:
> ```bash
> scripts/sync-7pace.sh \
>   --description "Descrição da atividade" \
>   --start "2026-01-14T14:00:00Z" \
>   --end "2026-01-14T16:00:00Z" \
>   --work-item-id 1234
> ```

## Migração de `.env` legado

Se o projeto tem `.claude/integrations/timetracking/.env` antigo, o script `sync-7pace.sh` ainda funciona via fallback. Para migrar:

1. Configurar env vars seguindo este setup
2. Validar que funciona (Passo 5)
3. Apagar o `.env` antigo: `rm .claude/integrations/timetracking/.env`
4. (Opcional) Apagar o diretório se vazio

## Referência rápida — Activity Types

Os GUIDs são do seu tenant do 7pace. Substitua os marcadores pelos valores de `GET /api/rest/activityTypes?api-version=3.2`.

| Nome              | ID                                     |
| ----------------- | -------------------------------------- |
| Desenvolvimento   | `<7PACE_ACTIVITY_ID_DESENVOLVIMENTO>`  |
| Operação          | `<7PACE_ACTIVITY_ID_OPERACAO>`         |
| Reunião           | `<7PACE_ACTIVITY_ID_REUNIAO>`          |
| Rituais Scrum     | `<7PACE_ACTIVITY_ID_RITUAIS_SCRUM>`    |
| Planejamento      | `<7PACE_ACTIVITY_ID_PLANEJAMENTO>`     |
| Homologação       | `<7PACE_ACTIVITY_ID_HOMOLOGACAO>`      |
| Treinamento       | `<7PACE_ACTIVITY_ID_TREINAMENTO>`      |

## Referência rápida — API

- **Base URL:** `https://<SEVENPACE_ORG>.timehub.7pace.com`
- **OData (leitura):** `GET /api/odata/v3.2/workLogsOnly`
- **REST (escrita):** `POST /api/rest/workLogs?api-version=3.2`
- **REST (atualização):** `PATCH /api/rest/workLogs/{id}?api-version=3.2`
- **REST (deleção):** `DELETE /api/rest/workLogs/{id}?api-version=3.2`
- **Auth:** `Authorization: Bearer {token}`
- **Campos obrigatórios (POST):** `workItemId`, `length` (segundos), `timestamp` (ISO 8601)
- **Campos opcionais:** `comment`, `activityTypeId`, `timeZone` (-180 para BRT)
