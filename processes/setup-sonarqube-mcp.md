---
name: setup-sonarqube-mcp
description: "Use quando o MCP Server do SonarQube não estiver configurado, ou quando precisar de análise de qualidade de código (code smells, bugs, vulnerabilidades) e o MCP não responder."
---

# Setup SonarQube MCP

Configura o MCP Server oficial do SonarQube para que a ferramenta de AI em uso possa analisar qualidade de código durante o code review. O token é mantido **fora do contexto do AI** via variável de ambiente.

## ⚠️ Regra crítica de segurança

**O usuário NUNCA deve colar o token na conversa com o AI.** O token transita apenas entre o usuário, o terminal e o destino final (Keychain, secret manager ou shell config). O config do MCP referencia `${SONARQUBE_TOKEN}` por nome, sem o valor.

Se em qualquer momento o usuário oferecer colar o token na conversa, **recusar** e redirecioná-lo a fazer no próprio terminal.

## Pré-requisitos

- Acesso ao SonarQube on-premise do time (`https://<SONARQUBE_URL>`) — pode requerer VPN

## Passo 1 — Gerar token do SonarQube

Apresente ao usuário:

> Você precisa gerar um token no SonarQube:
>
> 1. Acesse: https://<SONARQUBE_URL>/account/security
> 2. Em **Generate Tokens**, preencha:
>    - **Name:** `<sua-ferramenta-de-ai>` (ex: "Claude Code SonarQube MCP")
>    - **Type:** User Token
>    - **Expires in:** escolha a duração desejada
> 3. Clique em **Generate** e copie o token (formato: `squ_` seguido de 40 caracteres hex)
>
> **Não cole o token nesta conversa.** Você vai colá-lo no seu terminal nos próximos passos.

## Passo 2 — Escolher onde armazenar o token

Perguntar ao usuário:

> Onde você quer armazenar o token? Numere a opção:
>
> 1. **macOS Keychain** — encrypted at rest, integrado ao OS (recomendado para macOS)
> 2. **1Password CLI (`op`)**
> 3. **Bitwarden CLI (`bw`)**
> 4. **Direto em `~/.zshrc`** — token plain-text num arquivo seu (não passa pelo AI mesmo assim)
> 5. **Outro secret manager** — me diga qual

Aguardar resposta e prosseguir apenas com a opção escolhida.

## Passo 3 — Configurar conforme escolha

### Opção 1: macOS Keychain

> Cole estes comandos no seu terminal. O primeiro vai pedir o token interativamente:
>
> ```bash
> # Salvar no Keychain (-w sem valor faz prompt silencioso)
> security add-generic-password -s 'sonarqube-api-token' -a "$USER" -w
> ```
>
> Adicione ao `~/.zshrc`:
>
> ```bash
> # SonarQube MCP — token via macOS Keychain
> export SONARQUBE_TOKEN=$(security find-generic-password -s 'sonarqube-api-token' -w 2>/dev/null)
> export SONARQUBE_URL='https://<SONARQUBE_URL>'
> ```
>
> Recarregue: `source ~/.zshrc`

### Opção 2: 1Password CLI

> Cole no terminal:
>
> ```bash
> op whoami || op signin
> op item create --category='API Credential' --title='SonarQube' \
>   --vault='Personal' \
>   credential='[type-token-here]'
> ```
>
> Substitua `[type-token-here]` pelo token, ou use `op item edit` depois pra colar.
>
> Adicione ao `~/.zshrc`:
>
> ```bash
> # SonarQube MCP — token via 1Password
> export SONARQUBE_TOKEN=$(op read 'op://Personal/SonarQube/credential' 2>/dev/null)
> export SONARQUBE_URL='https://<SONARQUBE_URL>'
> ```
>
> Recarregue: `source ~/.zshrc`

### Opção 3: Bitwarden CLI

> Cole no terminal:
>
> ```bash
> bw login
> export BW_SESSION=$(bw unlock --raw)
> # Criar item via UI Bitwarden (mais simples) com nome 'SonarQube'
> ```
>
> Adicione ao `~/.zshrc`:
>
> ```bash
> # SonarQube MCP — token via Bitwarden
> export BW_SESSION=$(bw unlock --raw 2>/dev/null)
> export SONARQUBE_TOKEN=$(bw get notes 'SonarQube' 2>/dev/null)
> export SONARQUBE_URL='https://<SONARQUBE_URL>'
> ```
>
> Recarregue: `source ~/.zshrc`

### Opção 4: Direto em `~/.zshrc`

> Edite `~/.zshrc` adicionando (substitua `cole-o-token-aqui` pelo seu token):
>
> ```bash
> # SonarQube MCP
> export SONARQUBE_TOKEN='cole-o-token-aqui'
> export SONARQUBE_URL='https://<SONARQUBE_URL>'
> ```
>
> Recarregue: `source ~/.zshrc`
>
> **Para Windows (PowerShell):** edite `$PROFILE` usando `$env:SONARQUBE_TOKEN = '...'`.

### Opção 5: Outro secret manager

Padrão geral: armazenar na ferramenta sem expor na conversa, depois exportar via comando da ferramenta no `~/.zshrc`:

```bash
export SONARQUBE_TOKEN=$(<comando-da-ferramenta>)
export SONARQUBE_URL='https://<SONARQUBE_URL>'
```

## Passo 4 — Validar env vars (sem revelar token)

Após o usuário recarregar o shell:

```bash
[[ -n "${SONARQUBE_TOKEN}" ]] && echo "✓ SONARQUBE_TOKEN configurado" || echo "✗ SONARQUBE_TOKEN NÃO visível"
[[ -n "${SONARQUBE_URL}" ]] && echo "✓ SONARQUBE_URL: $SONARQUBE_URL" || echo "✗ SONARQUBE_URL NÃO visível"
```

> **Importante:** este comando só revela "set"/"not set", nunca o valor.

## Passo 5 — Gerar config do MCP via ferramenta oficial

A SonarQube mantém um **gerador oficial de configuração** que cobre todos os clientes (Claude Code, Cursor, VSCode + Copilot, Codex, etc.) e respeita variáveis de ambiente:

**🔗 https://mcp.sonarqube.com/config-generator.html**

Apresente ao usuário:

> Para gerar a configuração do MCP server específica para a sua ferramenta de AI:
>
> 1. Abra o gerador oficial: https://mcp.sonarqube.com/config-generator.html
> 2. **Target AI client:** selecione a ferramenta que você usa (Claude Code, Cursor, VSCode, etc.)
> 3. **SonarQube platform type:** "Self-Hosted (Server)"
> 4. **Instance URL:** `https://<SONARQUBE_URL>`
> 5. **Authentication / User token:** **DEIXE EM BRANCO** — isso preserva o placeholder `${SONARQUBE_TOKEN}` no output, fazendo o MCP ler do env var (sem hardcodar o token na config)
> 6. **Transport mode:** stdio (default — mais simples)
> 7. (Opcional) **Default project key:** `<PROJECT_KEY>` — facilita análises sem precisar especificar projeto
> 8. (Opcional) **Workspace mount path:** caminho absoluto do projeto (ex: `<PROJECT_ROOT>`) se a ferramenta usa Docker
> 9. Clique em "Generate" e copie o output
>
> Cole o output gerado no arquivo de config da sua ferramenta:
> - **Claude Code:** `~/.claude.json` na seção `mcpServers` do projeto
> - **Cursor:** `.cursor/mcp.json` ou Settings → Cursor Settings → MCP
> - **VSCode + Copilot:** `settings.json` na seção `github.copilot.chat.mcp.servers`
> - **Outras ferramentas:** consulte a documentação da ferramenta para o local exato
>
> ⚠️ A página gerada exibe um aviso: "Do not share this generated text with others if it contains your SonarQube user token." — Como você deixou o token em branco, **a config gerada NÃO contém o token literal** e é segura para colar/compartilhar.

## Passo 6 — Reiniciar a ferramenta de AI e testar

> Configuração salva. **Feche e reabra** a ferramenta de AI a partir de um terminal que tenha as env vars já exportadas (após `source ~/.zshrc` ou abrindo terminal novo).
>
> A ferramenta de AI precisa **herdar `SONARQUBE_TOKEN` do shell que a iniciou** para passar ao MCP server. Se você abriu a ferramenta antes de exportar a var, feche e reabra.

Após reiniciar, validar com duas operações de leitura:

1. **Listar projetos acessíveis** — deve retornar `<PROJECT_KEY>`
2. **Analisar arquivo conhecido** (ex: `<APP_DIR>/src/app/app.config.ts`) — deve retornar análise (mesmo que sem issues)

## Passo 7 — Confirmar

Se ambos os testes passaram:

> Setup do SonarQube MCP concluído.
>
> **Onde está o token:** [Keychain / 1Password / Bitwarden / ~/.zshrc]
> **Env vars:** `SONARQUBE_TOKEN`, `SONARQUBE_URL`
> **Config MCP:** gerada via ferramenta oficial, referencia `${SONARQUBE_TOKEN}` (sem valor literal)
> **AI nunca viu o valor do token.**
>
> O processo `phase-code-review` agora pode analisar arquivos modificados via SonarQube.

## Diagnóstico de erros comuns

| Sintoma                                  | Causa provável                                           | Solução                                                                                          |
| ---------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `401 Unauthorized`                       | Token inválido/expirado ou env var não chegou ao MCP     | `[[ -n "$SONARQUBE_TOKEN" ]]` no terminal; gerar novo token se necessário; reiniciar ferramenta de AI |
| `403 Forbidden`                          | Permissões insuficientes                                 | Verificar permissões do usuário no SonarQube                                                     |
| MCP tools `mcp__sonarqube__*` ausentes   | Ferramenta de AI não foi reiniciada / env não passou     | Fechar e reabrir a partir de terminal com env vars; conferir `printenv \| grep SONAR` no terminal |
| `Connection refused`                     | Sem acesso ao on-premise                                 | VPN do time pode ser necessária                                                                  |

## Capacidades cobertas

O MCP do SonarQube cobre (nomes exatos das tools variam por ferramenta de AI):

- Analisar arquivo individual (snippet ou path)
- Buscar issues existentes em projetos
- Métricas de cobertura, complexidade, etc.
- Status do quality gate
- Buscar hotspots de segurança

## Referência rápida

- **Server:** `https://<SONARQUBE_URL>` (on-premise do time)
- **Project Key:** `<PROJECT_KEY>`
- **Token format:** `squ_` + 40 hex chars
- **Token settings:** https://<SONARQUBE_URL>/account/security
- **Gerador oficial de config MCP:** https://mcp.sonarqube.com/config-generator.html

## Nota sobre `sonar verify` (CLI)

O comando `sonar verify` da CLI `sonarqube-cli` requer **SonarQube Cloud** e **não funciona** com o servidor on-premise do time. Sempre usar o MCP para análise automatizada.

## Opcional: hook de segredos do CLI `sonar`

O kit não inclui hook de detecção de segredos. Se você quiser que a ferramenta de AI seja bloqueada ao ler arquivos com segredos detectados, instale o CLI `sonar` da SonarSource (https://github.com/SonarSource/sonarqube-cli) e rode, no próprio projeto, o comando de integração do CLI com a sua ferramenta de AI, conforme a documentação do CLI. É o CLI que gera e registra o hook no projeto.

Este passo é opcional. O restante deste setup não depende dele.
