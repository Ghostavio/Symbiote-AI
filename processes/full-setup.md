---
name: full-setup
description: "Use quando o usuário precisar configurar o ambiente completo do projeto em uma nova máquina, ou quando ferramentas essenciais (plugins Claude Code, MCP Azure DevOps, MCP SonarQube, 7pace) estiverem ausentes."
---

# Full Setup — Ambiente de Desenvolvimento

Configura o ambiente completo para desenvolvimento no projeto com Claude Code, incluindo ferramentas do sistema, plugins essenciais e integrações com Azure DevOps, SonarQube e 7pace Timetracker.

## Hard Gate

<HARD-GATE>
NÃO pule etapas — execute cada uma em ordem.
Pergunte ao usuário antes de instalar qualquer ferramenta do sistema.
Se uma etapa falhar, diagnostique antes de prosseguir.
</HARD-GATE>

## Fluxo

```
Detectar OS e gerenciador de pacotes
       |
       v
Ferramentas do sistema (gh, fzf, etc.)
       |
       v
Plugins essenciais do Claude Code
       |
       v
Setup Azure DevOps MCP (/setup-azure-mcp)
       |
       v
Setup SonarQube MCP (/setup-sonarqube-mcp)
       |
       v
Setup 7pace Timetracker (/setup-7pace)
       |
       v
Verificação final
```

---

### Passo 1 — Detectar ambiente

Detectar OS e gerenciador de pacotes disponível:

```bash
uname -s 2>/dev/null || echo "Windows"  # Darwin (macOS), Linux, ou Windows
```

No Windows, também verificar via PowerShell:
```powershell
$env:OS  # Windows_NT
```

Identificar o gerenciador de pacotes:
- **macOS:** `brew` (Homebrew) — verificar com `which brew`
- **Windows:** `winget` (App Installer) — verificar com `winget --version`
- **Windows (alternativa):** `choco` (Chocolatey) — verificar com `choco --version`
- **Windows (alternativa):** `scoop` — verificar com `scoop --version`
- **Linux (Debian/Ubuntu):** `apt` — verificar com `which apt`
- **Linux (Fedora/RHEL):** `dnf` — verificar com `which dnf`
- **Linux (Arch):** `pacman` — verificar com `which pacman`

Se nenhum gerenciador for encontrado:
- **macOS:** Orientar instalação do Homebrew:
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
- **Windows:** `winget` vem pré-instalado no Windows 10 1709+ e Windows 11. Se não estiver disponível, orientar instalar o [App Installer](https://apps.microsoft.com/detail/9nblggh4nns1) pela Microsoft Store.

Verificar também:
- `node --version` (requerido, mínimo v18)
- `npm --version` ou `yarn --version`
- `docker --version` (necessário para SonarQube MCP)
- `git --version`

---

### Passo 2 — Ferramentas do sistema

Apresentar ao usuário a lista de ferramentas recomendadas e perguntar quais deseja instalar:

> **Ferramentas recomendadas para o workflow do projeto:**
>
> | Ferramenta | Descrição | Status |
> |------------|-----------|--------|
> | `gh` | GitHub CLI — PRs, issues, code review | [instalado/não instalado] |
> | `fzf` | Fuzzy finder — busca rápida em arquivos e histórico | [instalado/não instalado] |
> | `jq` | Processador JSON — útil para scripts e debugging de API | [instalado/não instalado] |
> | `tsx` | TypeScript executor — útil para MCP servers locais | [instalado/não instalado] |
> | `docker` | Container runtime — necessário para SonarQube MCP | [instalado/não instalado] |
> | `rtk` | [Rust Token Killer](https://github.com/rtk-ai/rtk) — proxy CLI que comprime saídas de Bash 60-90% antes do contexto do AI. Ativa via PreToolUse hook (`rtk hook claude`). | [instalado/não instalado] |
> | `scm_breeze` | [SCM Breeze](https://github.com/scmbreeze/scm_breeze) — atalhos de git/shell (numbered file shortcuts, repo index, aliases curtos). Útil quando o agente vai interagir com git intensivamente. | [instalado/não instalado] |
>
> Quais você gostaria de instalar? (ex: "todas", "gh e fzf", "nenhuma")

Para cada ferramenta que o usuário aceitar, instalar com o gerenciador detectado:

**macOS (Homebrew):**
```bash
brew install gh fzf jq rtk
npm install -g tsx
# scm_breeze (não está no brew):
git clone https://github.com/scmbreeze/scm_breeze.git ~/.scm_breeze && ~/.scm_breeze/install.sh
```

Após instalar o RTK, ativar o hook na ferramenta de AI em uso. O comando padrão é `rtk init -g`, mas o flag varia por ferramenta:

```bash
rtk init -g                     # Claude Code / Copilot (default)
rtk init -g --gemini            # Gemini CLI
rtk init -g --codex             # Codex (OpenAI)
rtk init --agent cursor         # Cursor
rtk init --agent windsurf       # Windsurf
rtk init --agent cline          # Cline / Roo Code
rtk init --agent kilocode       # Kilo Code
rtk init --agent antigravity    # Google Antigravity
```

Se rodar não-interativamente, adicionar o hook manualmente conforme o formato de configuração da ferramenta. Para Claude Code, em `~/.claude/settings.json`:

```json
"hooks": {
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{ "type": "command", "command": "rtk hook claude" }]
  }]
}
```

Depois **reiniciar a ferramenta de AI** para o hook entrar em vigor. Validar com qualquer comando Bash — output deve aparecer comprimido. Para auditoria: `rtk gain --history`.

**Windows (winget):**
```powershell
winget install --id GitHub.cli -e
winget install --id junegunn.fzf -e
winget install --id jqlang.jq -e
npm install -g tsx
# RTK no Windows: extrair https://github.com/rtk-ai/rtk/releases/latest → rtk-x86_64-pc-windows-msvc.zip
# colocar rtk.exe em PATH e rodar `rtk init -g`. Para experiência completa, prefira WSL.
```

**Windows (Chocolatey):**
```powershell
choco install gh fzf jq -y
npm install -g tsx
```

**Windows (Scoop):**
```powershell
scoop install gh fzf jq
npm install -g tsx
```

**Linux (apt):**
```bash
sudo apt update && sudo apt install -y gh fzf jq
npm install -g tsx
# RTK (binary release):
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
rtk init -g
# scm_breeze:
git clone https://github.com/scmbreeze/scm_breeze.git ~/.scm_breeze && ~/.scm_breeze/install.sh
```

**Linux (dnf):**
```bash
sudo dnf install -y gh fzf jq
npm install -g tsx
```

**Linux (pacman):**
```bash
sudo pacman -S --noconfirm github-cli fzf jq
npm install -g tsx
```

Após instalar, verificar cada uma:
```bash
gh --version
fzf --version
jq --version
tsx --version
rtk --version
[ -d ~/.scm_breeze ] && echo "scm_breeze ✓"
```

> **Nota Windows:** Se estiver usando PowerShell e algum comando não for reconhecido após a instalação, fechar e reabrir o terminal para atualizar o PATH.

---

### Passo 3 — Plugins / extensões essenciais da ferramenta de AI

#### Superpowers (multi-plataforma)

O **Superpowers** (https://github.com/obra/superpowers) é o conjunto de skills de workflow (brainstorming, planning, code review, TDD, debugging, executing-plans, etc.) usado neste projeto. Suporta múltiplas ferramentas:

| Ferramenta              | Comando de instalação                                                        |
| ----------------------- | ---------------------------------------------------------------------------- |
| **Claude Code**         | `/plugin install superpowers@claude-plugins-official` (marketplace oficial)  |
| **Cursor**              | `/add-plugin superpowers` no Agent chat (ou via plugin marketplace)          |
| **OpenAI Codex**        | Buscar "Superpowers" via interface `/plugins`                                |
| **GitHub Copilot CLI**  | Registrar marketplace, depois `copilot plugin install`                       |
| **Gemini CLI**          | `gemini extensions install` direto do repo                                   |
| **OpenCode**            | Seguir instruções no arquivo de config do projeto                            |

Consultar https://github.com/obra/superpowers/blob/main/README.md para detalhes atualizados.

#### Outras integrações

| Capacidade                | Claude Code                              | Cursor                                | VSCode + Copilot                                  | Codex / Antigravity                  |
| ------------------------- | ---------------------------------------- | ------------------------------------- | ------------------------------------------------- | ------------------------------------ |
| Browser automation (E2E)  | `playwright@claude-plugins-official`     | Playwright MCP via `.cursor/mcp.json` | Playwright MCP via `settings.json`                | Playwright MCP                       |
| Language Server (LSP)     | Plugin LSP da stack (ex.: `typescript-lsp@claude-plugins-official`) | Built-in / extensão da stack          | Built-in / extensão da stack                      | Tool-dependent                       |

#### Comandos de instalação por ferramenta (Claude Code)

```bash
claude plugin marketplace add https://registry.claude.ai/marketplace
claude plugin install superpowers@claude-plugins-official
claude plugin install playwright@claude-plugins-official
claude plugin install typescript-lsp@claude-plugins-official
```

Se algum plugin falhar:
1. Verificar se o marketplace foi adicionado corretamente
2. Pedir ao usuário para executar `! claude plugin marketplace add https://registry.claude.ai/marketplace` (o `!` executa na sessão)
3. Tentar novamente a instalação
4. Se persistir, pedir ao usuário para reiniciar a sessão ou executar `/reload-plugins`

#### Para outras ferramentas

- **Cursor:** Playwright MCP em `.cursor/mcp.json`. Superpowers via `/add-plugin superpowers`.
- **VSCode + Copilot:** Playwright MCP em `settings.json` (`github.copilot.chat.mcp.servers`). Superpowers via Copilot CLI.
- **Codex / Antigravity:** Superpowers via `/plugins`. Playwright MCP conforme doc da ferramenta.
- **Gemini CLI:** `gemini extensions install` direto do repo do Superpowers.

Após instalar/configurar, informar:

> **Capacidades configuradas:**
> - **Superpowers** — brainstorming, planning, code review, TDD, debugging, executing-plans, etc.
> - **Playwright MCP** — automação de browser (testes E2E, validação visual)
> - **Language Server (LSP) da stack** — análise e navegação de código

---

### Passo 4 — Setup Azure DevOps MCP

Invocar a skill `setup-azure-mcp`:

> Agora vamos configurar a integração com o Azure DevOps para interagir com work items, boards e pull requests.

Seguir o fluxo da skill `setup-azure-mcp` (configurar MCP no `~/.claude.json`, autenticação via browser, testar conexão).

---

### Passo 5 — Setup SonarQube MCP

Verificar se o Docker está rodando antes de prosseguir:

```bash
docker info > /dev/null 2>&1 && echo "Docker OK" || echo "Docker NÃO está rodando"
```

Se Docker não estiver rodando:
> O SonarQube MCP requer Docker. Deseja pular este passo e configurar depois? (s/n)
> Se sim, você pode executar `/setup-sonarqube-mcp` a qualquer momento.

Se Docker estiver disponível, invocar a skill `setup-sonarqube-mcp`:

> Agora vamos configurar a análise de qualidade de código via SonarQube.

Seguir o fluxo da skill `setup-sonarqube-mcp` (gerar token, configurar MCP com Docker, testar análise).

Opcional: o hook que bloqueia a leitura de arquivos com segredos não vem no kit. Quem quiser roda, no próprio projeto, o comando de integração do CLI `sonar` (ver a seção "Opcional: hook de segredos do CLI `sonar`" no `setup-sonarqube-mcp`).

---

### Passo 6 — Setup 7pace Timetracker

Invocar a skill `setup-7pace`:

> Por último, vamos configurar o registro automático de horas no 7pace Timetracker.

Seguir o fluxo da skill `setup-7pace` (gerar token, guardar o token fora do contexto da IA e exportar `SEVENPACE_API_TOKEN` e `SEVENPACE_BASE_URL`, testar criação/deleção de worklog).

---

### Passo 7 — Verificação final

Apresentar resumo do que foi configurado:

> ## Setup completo!
>
> | Item | Status |
> |------|--------|
> | **Ferramentas do sistema** | [lista do que foi instalado] |
> | **RTK (Rust Token Killer)** | [OK / não instalado / hook ativo?] |
> | **SCM Breeze** | [OK / não instalado] |
> | **Superpowers** (multi-plataforma) | [OK/não instalado] |
> | **Playwright MCP / plugin** | [OK/não instalado] |
> | **TypeScript LSP / language server** | [OK/não instalado] |
> | **Azure DevOps MCP** | [OK/pulado] |
> | **SonarQube MCP** | [OK/pulado — Docker necessário] |
> | **7pace Timetracker** | [OK/pulado] |
>
> **Próximos passos:**
> - Leia `templates/project-reference.template.md` para entender a arquitetura
> - Use `/spec-builder` para criar especificações de novas features
> - Use o workflow documentado em `docs/workflow.md` como referência
> - Para items pulados, execute a skill correspondente a qualquer momento:
>   - `/setup-azure-mcp`
>   - `/setup-sonarqube-mcp`
>   - `/setup-7pace`

---

## Notas

- Este setup é idempotente — rodar novamente não causa problemas (ferramentas já instaladas são detectadas e puladas)
- Cada skill de setup pode ser executada individualmente a qualquer momento
- As credenciais ficam em `~/.claude.json` (MCP servers) e, para o 7pace, no local escolhido no `setup-7pace` (Keychain, 1Password, Bitwarden ou `~/.7pace`), todos fora do git
