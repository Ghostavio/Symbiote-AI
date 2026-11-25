---
name: setup-azure-mcp
description: "Use quando o MCP Server do Azure DevOps não estiver configurado para a ferramenta de AI em uso (Claude Code, Cursor, Codex, VSCode/Copilot, etc.)."
---

# Setup Azure DevOps MCP

Configura o MCP Server oficial do Azure DevOps (mantido pela Microsoft) para que a ferramenta de AI em uso possa interagir diretamente com work items, boards, pull requests e pipelines da organização.

## Passo 1 — Seguir a documentação oficial da Microsoft

A configuração do MCP varia por ferramenta (Claude Code, Cursor, Codex, VSCode/Copilot, etc.) e a Microsoft mantém um guia atualizado cobrindo todas elas:

**📖 https://github.com/microsoft/azure-devops-mcp/blob/main/docs/GETTINGSTARTED.md**

Leia o documento, identifique a sua ferramenta e siga as instruções de instalação correspondentes. Se a ferramenta não estiver listada, procure pela seção "Generic" ou tente a configuração mais próxima (a maioria segue o mesmo padrão de `npx @azure-devops/mcp <organization>`).

**Dados específicos do time para preencher na configuração:**

| Campo                     | Valor                              |
| ------------------------- | ---------------------------------- |
| Organization              | `<AZURE_ORG>`                          |
| URL                       | `https://<AZURE_ORG>.visualstudio.com` |
| Projeto principal         | `<AZURE_PROJECT>`                  |
| Área                      | `<AREA_PATH>`                      |

A autenticação é via login interativo no browser (Microsoft Entra ID) — não precisa de PAT manual.

## Passo 2 — Escolher Projeto e Área default

Perguntar ao usuário quais Projeto e Área serão usados como padrão nas operações desta sessão (criação de work items, buscas, etc.):

> Qual **Projeto** do Azure DevOps você vai usar? Informe o nome exato (`<AZURE_PROJECT>`).

> Qual **Área** dentro do projeto? Informe o caminho completo (`<AREA_PATH>`).

**Armazenar a escolha** no mecanismo de memória/contexto persistente da ferramenta em uso (auto-memory no Claude Code, contexto do AGENTS.md no Codex/Antigravity, regra "Always" no Cursor, instructions adicional no Copilot).

Esta informação será usada por todos os processos que criam/buscam work items (`create-work-item`, `start-workflow`, etc.).

## Passo 3 — Testar conexão

Após configurar e (se necessário) reiniciar a ferramenta, validar que a integração funciona. Cada ferramenta expõe os mesmos verbos sob nomes diferentes; faça duas operações de leitura simples:

1. **Listar projetos da organização** — deve retornar o projeto escolhido no Passo 2 (`<AZURE_PROJECT>`) entre os resultados
2. **Buscar um work item conhecido** — pedir ao usuário um ID que ele conheça (ex: o WI de "Outras Atividades" da equipe, ou qualquer WI ativo no Board); a operação deve retornar os dados do work item

Se ambas funcionarem, a integração está OK.

## Passo 4 — Confirmar ao usuário

Ao final, informar:

> Integração com Azure DevOps configurada com sucesso.
>
> Os processos `create-work-item`, `start-workflow` e `phase-code-review` agora podem criar/atualizar work items, vincular PRs e consultar o Board.

## Capacidades cobertas (independente de ferramenta)

O MCP oficial do Azure DevOps cobre:

- **Work Items:** criar, atualizar, buscar, vincular pai-filho, listar por iteração
- **Repositórios e Pull Requests:** criar/atualizar PR, comentários, threads
- **Pipelines:** listar runs, builds, artefatos, logs
- **Core:** listar projetos, times, áreas, iterações
- **Search:** buscar work items por texto, código, wiki

Os nomes exatos das ferramentas (ex: `mcp__azure-devops__wit_create_work_item` no Claude Code) variam por ferramenta — consulte a doc oficial linkada acima ou use o tool listing da sua ferramenta para descobrir.

## Referência — Organização

- **Organização:** `<AZURE_ORG>`
- **URL:** https://<AZURE_ORG>.visualstudio.com
- **Projeto principal:** `<AZURE_PROJECT>` (escolhido no Passo 2)
- **Área:** `<AREA_PATH>` (escolhida no Passo 2)

> IDs específicos de work items (Feature umbrella, WI de "Outras Atividades", etc.) variam por equipe/projeto e devem ser armazenados no mecanismo de memória/contexto da ferramenta de AI em uso (não hardcoded nesta skill).
