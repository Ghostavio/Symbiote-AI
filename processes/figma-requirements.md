---
name: figma-requirements
description: "Use quando o usuário quiser levantar requisitos de uma feature a partir de um design no Figma (via MCP, local ou online) — extrair telas, componentes, estados, textos e tokens e transformá-los num documento de requisitos que alimenta o spec-builder."
---

# Figma Requirements — Levantamento de Requisitos a partir do Figma (MCP)

Extrai a intenção de um design no Figma via **MCP** (Model Context Protocol) e a transforma num **documento de requisitos** estruturado, pronto para alimentar a skill `spec-builder`. Suporta tanto um servidor MCP **local** (Figma Desktop, Dev Mode) quanto **online** (MCP hospedado da Figma ou MCP community baseado na API REST).

## Quando usar

- O usuário tem um protótipo/design no Figma e quer iniciar uma feature a partir dele.
- Antes do `spec-builder` no Fluxo A (Nova Feature) do `start-workflow`, quando há design pronto.
- Para sincronizar uma spec existente com mudanças de design.

## Pré-requisito: um servidor MCP de Figma configurado

Detecte/escolha **uma** das opções abaixo (a skill tenta a local primeiro, depois a online):

### Opção A — Local (Figma Desktop, Dev Mode MCP Server) — recomendado se você edita no desktop

1. Abra o **app desktop do Figma** (o MCP local não funciona no Figma web) e abra o arquivo de design.
2. Menu **Figma → Preferences → "Enable Dev Mode MCP Server"** (requer assento com Dev Mode — Dev ou Full — em plano pago).
3. O servidor sobe em `http://127.0.0.1:3845/mcp` (SSE/HTTP local).
4. Registre o MCP (exemplo Claude Code):
   ```bash
   claude mcp add --transport sse figma-dev-mode http://127.0.0.1:3845/sse
   # (versões recentes do Figma usam o endpoint /mcp via HTTP streamable)
   ```
   Ou via `.mcp.json` do projeto:
   ```json
   { "mcpServers": { "figma-dev-mode": { "type": "sse", "url": "http://127.0.0.1:3845/sse" } } }
   ```
   Ferramentas típicas: `get_code`, `get_variable_defs` (tokens/variáveis), `get_image`/`get_screenshot`, `get_metadata`, `get_code_connect_map`. Operam sobre a **seleção atual** no Figma ou sobre um `nodeId`.

### Opção B — Online (MCP hospedado da Figma) — recomendado se não usa o desktop

1. MCP remoto oficial em `https://mcp.figma.com/mcp` (autenticação OAuth, sem app local).
   ```bash
   claude mcp add --transport http figma https://mcp.figma.com/mcp
   # depois autentique com /mcp (fluxo OAuth no navegador)
   ```
2. Opera sobre **URLs de arquivo/nó** do Figma (cole o link do frame).

### Opção C — Online (MCP community via API REST) — alternativa sem OAuth

1. Gere um token em **Figma → Settings → Security → Personal access tokens**.
2. Registre o MCP (ex.: Framelink `figma-developer-mcp`) via `.mcp.json`:
   ```json
   { "mcpServers": { "figma": {
       "command": "npx",
       "args": ["-y", "figma-developer-mcp", "--figma-api-key=${FIGMA_API_KEY}", "--stdio"]
   } } }
   ```
   `FIGMA_API_KEY` vem de variável de ambiente (NUNCA hardcode o token). Ferramenta principal: `get_figma_data({ fileKey, nodeId })`, `download_figma_images`.

> **Mapeamento de tool-calls por ferramenta de IA:** ver [`ai-tools-matrix.md`](../ai-tools-matrix.md). Os exemplos abaixo usam nomes do Claude Code (`mcp__figma-dev-mode__*` / `mcp__figma__*`); em Cursor/Codex/Copilot use os equivalentes registrados.

## Processo

### Passo 1 — Obter o alvo no Figma

Pergunte ao usuário (ou detecte):
- **Local (Opção A):** peça para ele **selecionar o frame/página** no Figma desktop. A skill opera sobre a seleção atual.
- **Online (B/C):** peça a **URL do frame** (ex.: `https://www.figma.com/design/<fileKey>/...?node-id=<nodeId>`). Extraia `fileKey` e `nodeId` da URL.

Confirme o escopo: uma tela, um fluxo (várias telas) ou um sistema inteiro? Para fluxos, processe tela a tela.

### Passo 2 — Extrair o design

Para cada tela/frame no escopo, colete via MCP:

1. **Imagem de referência** (`get_image`/`get_screenshot` ou `download_figma_images`) — para validação visual e para o usuário confirmar que está olhando o frame certo.
2. **Estrutura e metadados** (`get_metadata` / `get_figma_data`) — hierarquia de nós, nomes de camadas, componentes e instâncias, variantes (estados: default/hover/disabled/loading/error/empty), auto-layout.
3. **Conteúdo de texto** — todos os textos visíveis (labels, placeholders, mensagens, títulos, CTAs) — fonte de verdade para microcopy e i18n.
4. **Tokens/variáveis** (`get_variable_defs`) — cores, tipografia, spacing, raios — para casar com o design system do projeto.
5. **Código de referência** (`get_code`, se disponível) — representação da seleção; use como pista de estrutura, NÃO como implementação final.
6. **Interações/prototyping** — links de navegação entre frames, gestos, transições (quando expostos).
7. **Anotações de Dev Mode / dev resources** — anotações, measurements e links que designers deixaram para devs.

### Passo 3 — Entrevista de elicitação (preencher o que o design não diz)

O design mostra o "o quê visual", mas raramente o "comportamento/dados". Pergunte **uma por vez**, pulando o que o design já responde:

- **Origem dos dados:** cada campo/lista vem de qual endpoint/entidade? Há contrato de API?
- **Estados não desenhados:** loading, vazio, erro, sem permissão, paginação, offline — existem? Como se comportam?
- **Validações:** regras por campo (obrigatório, formato, máscara, limites). Mensagens de erro.
- **Permissões/roles:** quem vê/usa cada ação? Há ações destrutivas que pedem confirmação?
- **Responsividade:** breakpoints, comportamento mobile/desktop (o frame cobre todos?).
- **Acessibilidade:** labels, navegação por teclado, contraste, foco.
- **Aceite:** qual o critério de "pronto" para cada tela/ação? (vira acceptance criteria EARS).

### Passo 4 — Gerar o documento de requisitos

Produza `docs/requisitos/<feature>-requisitos.md` (ou na plataforma externa — ver [`docs-target.md`](docs-target.md)) com:

- **Visão geral** da feature e link(s) do Figma (fileKey/nodeId).
- **Inventário de telas** — uma seção por tela: screenshot, componentes, estados, textos, tokens usados.
- **Requisitos funcionais** em formato **EARS** ("Quando <gatilho>, o sistema DEVE <resposta>").
- **Requisitos de dados** — entidades, campos, origens (endpoints), validações.
- **Regras de negócio, permissões, estados de borda e acessibilidade.**
- **Critérios de aceite** por tela/ação.
- **Pendências/decisões em aberto** levantadas na entrevista.

### Passo 5 — Handoff para o spec-builder

Apresente o documento ao usuário para revisão. Após aprovação, invoque **`spec-builder`** passando o documento de requisitos como entrada — ele usa o template em [`templates/spec-template.md`](../templates/spec-template.md) para produzir a spec completa. Em seguida, siga o `start-workflow` (Fluxo A).

## Boas práticas

- **Valide visualmente:** sempre traga o screenshot do frame e confirme com o usuário antes de extrair requisitos — evita levantar requisito da tela errada.
- **Não trate `get_code` como implementação** — é pista de estrutura; a implementação segue os padrões do projeto (ver `templates/project-reference.template.md`).
- **Tokens → design system:** mapeie variáveis do Figma para os tokens/tema do projeto em vez de hardcodar valores.
- **Segredos:** `FIGMA_API_KEY`/OAuth nunca entram em arquivo versionado — use variáveis de ambiente.
