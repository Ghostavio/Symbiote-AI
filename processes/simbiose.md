---
name: simbiose
description: "Use para aplicar o Symbiote-AI a um projeto existente ou iniciar um projeto novo com o kit."
---

# Simbiose — Aplicar o Symbiote-AI

Use primeiro a intenção explícita do usuário. Na ausência dela, inspecione o diretório **de destino** indicado no pedido, ou o diretório atual como contexto. Faça essa inspeção sem alterar arquivos. Se dois sinais apontarem para caminhos diferentes, dê preferência ao pedido explícito.

- **Projeto existente:** quando o usuário quiser adotar o kit em um projeto existente ou o destino tiver sinais claros de um projeto, como código, manifestos de dependências ou configuração de build, siga [o procedimento de integração](integrar.md) no destino. Se o kit ainda estiver em outro diretório, inclua no plano de integração os arquivos a copiar e como preservar as configurações existentes. Use a lista de instalação do Passo 3 como referência e aplique a cópia após a aprovação do plano.
- **Projeto novo:** quando o usuário pedir para criar um projeto, ou já tiver indicado um destino vazio ou ainda inexistente para a criação, siga os passos abaixo. Uma chamada pelo alias legado `scaffold` indica criação de um projeto novo, salvo instrução em contrário.
- **Contexto ambíguo:** um diretório que contém só `.git`, um README ou os arquivos do próprio kit pode ser um projeto começado ou um ponto de partida. Se a intenção e os sinais disponíveis não resolverem a dúvida, pergunte: “Você quer aplicar o Symbiote-AI a um projeto existente ou iniciar um projeto novo?” Aguarde a resposta antes de alterar arquivos.

## Criar um projeto novo

<HARD-GATE>
Confirme TODAS as escolhas (stack, nome, local) e mostre o plano antes de gerar qualquer coisa. NUNCA gere dentro de um diretório não-vazio sem confirmação explícita. Rode `git init` cedo para que tudo seja revisável/reversível.
</HARD-GATE>

## Passo 1 — Coletar o básico (uma pergunta por vez)

1. **Nome do projeto** e diretório destino.
2. **Tipo/stack:** ex.: Frontend (Angular / React+Vite / Next.js / Vue), Backend (.NET / Spring / NestJS / FastAPI / Go), Mobile, CLI, lib. Ofereça opções comuns; aceite "outro".
3. **Gerenciador de pacotes** preferido (yarn/npm/pnpm/bun, maven/gradle, uv/poetry…).
4. **Tracker** (Azure DevOps / Jira / GitHub Issues / nenhum), **time tracking** (7pace / Clockify / Toggl / Harvest / nenhum) e **destino de docs** (repo / Confluence / Outline / Notion) — as mesmas dimensões do `integrar`.
5. **Ferramentas de IA** que o time usa (Claude Code / Cursor / Codex / Antigravity / Copilot / Gemini) → quais wrappers manter.
6. **Adaptadores opcionais** (`adapters/` — ver `adapters/README.md` no kit): verifique se existem adaptadores compatíveis de stack, cloud ou observabilidade (ex.: `adapters/stacks/angular/`) e confirme quais acoplar ao projeto.

## Passo 2 — Gerar o esqueleto da aplicação (use o scaffolder do ecossistema)

Não reinvente: chame o gerador oficial do stack escolhido. Exemplos:

| Stack | Comando de scaffold |
|---|---|
| Angular | `npx @angular/cli new <nome>` |
| React + Vite | `npm create vite@latest <nome> -- --template react-ts` |
| Next.js | `npx create-next-app@latest <nome>` |
| Vue | `npm create vue@latest <nome>` |
| NestJS | `npx @nestjs/cli new <nome>` |
| .NET API | `dotnet new webapi -n <nome>` |
| Spring | `spring init --dependencies=web <nome>` (ou start.spring.io) |
| FastAPI | `uv init <nome>` + deps |
| Go | `go mod init <módulo>` |

Confirme o comando com o usuário antes de rodar. Se ele já tem um boilerplate/template próprio, use-o em vez do gerador padrão.

## Passo 3 — Instalar o kit no projeto novo

Copie a estrutura do kit para a raiz do projeto recém-criado (sem `.env`):

```
.agents/   .claude/   .cursor/   .github/copilot-instructions.md   AGENTS.md   GEMINI.md
processes/   templates/   docs/   scripts/   ai-tools-matrix.md   GUIA-DE-EXPANSAO.md
```

Crie um `.gitignore` que ignore `.env` e segredos (e adicione as entradas do stack geradas pelo scaffolder). Se adaptadores em `adapters/` tiverem sido selecionados no Passo 1, copie apenas as pastas dos adaptadores aprovados (ex.: `adapters/stacks/angular/`) — sem carregar adaptadores de outras stacks.

## Passo 4 — Especializar com `integrar`

Aplique [o procedimento de integração](integrar.md) ao projeto recém-criado, reaproveitando as escolhas do Passo 1. Ele:
- substitui os placeholders (`<PROJECT_KEY>`, `<TEST_CMD>`, `<src>`, …) pelos valores reais do projeto recém-criado;
- acopla os adaptadores selecionados (convenções em `.claude/PROJECT_REFERENCE.md`, checks em `phase-code-review` e presets opcionais de editor/skills);
- mantém só os wrappers das ferramentas de IA escolhidas;
- configura os MCPs (tracker, qualidade, docs, Figma, Playwright);
- preenche `templates/project-reference.template.md` → `.claude/PROJECT_REFERENCE.md`;
- ajusta o time tracking e o destino de docs.

## Passo 5 — Baseline + primeiro commit

1. Convenções: confirme lint/format/test configurados (o scaffolder normalmente já traz).
2. (Opcional) Stub de CI apontando para `<TEST_CMD>`/`<LINT_CMD>`/`<BUILD_CMD>`.
3. (Opcional) Crie o **épico/feature inicial** no tracker (skill `create-work-item`).
4. `git add -A && git commit` com a mensagem inicial (sem `Co-Authored-By`).

## Passo 6 — Próximos passos

- Rode `full-setup` para instalar ferramentas de sistema e plugins na máquina.
- Rode os `setup-*` necessários (`setup-azure-mcp`/`setup-jira`, `setup-sonarqube-mcp`, `setup-7pace`) e autentique os MCPs.
- Comece a desenvolver com `start-workflow` (use o **Fluxo Express** para as primeiras mudanças pequenas).

> **Segredos:** nada de token em arquivo versionado — preencha `.env` a partir do `.env.example` e confirme que o `.gitignore` cobre `.env`.
