---
name: docs-target
description: "Use para definir ONDE a documentação de processo (discovery, design, plano, diário, post-mortem, requisitos) é gravada — no repositório (in-repo) ou numa plataforma externa (Confluence, Outline, Notion) para manter os PRs limpos, contendo só código."
---

# Documentation Target — Onde mora a documentação de processo

Os fluxos do kit (`start-workflow`, `spec-builder`, `figma-requirements`, `phase-code-review`) produzem bastante documentação: discovery, brainstorm, design técnico, plano de implementação, diário, post-mortem, relatórios, requisitos. Por padrão esses arquivos vão para o **repositório**. Times que preferem **PRs enxutos** podem direcioná-los a uma **plataforma externa**.

## Os dois modos

| Modo | Onde a doc vive | Prós | Contras |
|---|---|---|---|
| **`repo`** (default) | `docs/**` versionado no Git | Versionado junto do código; offline; diff revisável | Polui o PR com arquivos `.md`; doc espalhada por repos |
| **`external`** | Confluence / Outline / Notion / etc. | **PRs só com código**; doc centralizada e pesquisável; melhor p/ stakeholders não-técnicos | Requer MCP/credenciais; doc desacoplada do commit |

No modo `external`, o fluxo **cria/atualiza a página na plataforma** e coloca a **URL** no work item e na descrição do PR — nenhum arquivo de doc de processo é commitado. (Código, testes e o `CHANGELOG`/`README` do projeto continuam no repo normalmente.)

## Configuração

Defina `DOC_TARGET` (e o destino) — perguntado pela skill `integrar` (passo 2.4) e registrável no `.env.example`/config do projeto:

```bash
DOC_TARGET=repo            # repo | confluence | outline | notion
# Para external, conforme a plataforma:
CONFLUENCE_SPACE_KEY=<SPACE>          # via MCP Atlassian (ver setup-jira, opção A)
OUTLINE_BASE_URL=https://app.getoutline.com/api  # ou a URL da sua instância self-hosted
OUTLINE_COLLECTION_ID=<COLLECTION>
NOTION_PARENT_PAGE_ID=<PAGE>
# Tokens (NUNCA versionar): CONFLUENCE_API_TOKEN / OUTLINE_API_KEY / NOTION_API_TOKEN
```

## Como publicar em cada plataforma

- **Confluence** — via o **MCP oficial da Atlassian** (mesmo da skill `setup-jira`, opção A): criar/atualizar página (`createConfluencePage`/`updateConfluencePage`) no espaço `CONFLUENCE_SPACE_KEY`. Ótimo se você já usa Jira.
- **Outline** — API REST (sem MCP). Auth `Authorization: Bearer $OUTLINE_API_KEY`; todos os endpoints são `POST` com body JSON. Principais:
  - Criar: `POST $OUTLINE_BASE_URL/documents.create` `{"collectionId","title","text"}` (text em markdown)
  - Atualizar: `POST .../documents.update` `{"id","text"}` · Buscar: `POST .../documents.search` `{"query"}`
  - Listar coleções: `POST .../collections.list` · Estrutura: `POST .../collections.documents` `{"id"}`
- **Notion** — via MCP do Notion (criar página filha de `NOTION_PARENT_PAGE_ID` com o conteúdo em blocks) ou a API oficial.

## Convenção para os fluxos (modo external)

1. Onde um fluxo gravaria `docs/<algo>.md`, em vez disso **publique na plataforma** e capture a URL retornada.
2. Registre a URL no **work item** (campo/coment) e na **descrição do PR** (seção "Documentação").
3. Mantenha apenas um stub mínimo no repo **se** o time quiser um ponteiro (ex.: `docs/README.md` listando os links) — opcional.
4. O **diário de implementação** continua incremental (Princípio 12 do `start-workflow`), só que como página viva na plataforma.

> Decisão tomada uma vez por projeto (via `integrar`). Na dúvida, comece com `repo` e migre para `external` quando o volume de doc começar a poluir os PRs.
