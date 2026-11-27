# Adaptadores do Symbiote-AI (`adapters/`)

O core do **Symbiote-AI** (`processes/`, `AGENTS.md`, `GEMINI.md`, wrappers e `.cursor/settings.json`) é **neutro de stack**. Especializações por tecnologia, nuvem ou observabilidade vivem aqui como **adaptadores opcionais e composíveis**, acoplados seletivamente via `simbiose` (e seu procedimento de integração em [`processes/integrar.md`](../processes/integrar.md)).

Um mesmo projeto pode combinar adaptadores ortogonais (por exemplo: `stacks/angular` + `cloud/aws` + `observability/<id>`, ou `stacks/react` + `cloud/cloudflare`).

## Estrutura de categorias

```text
adapters/
├── stacks/          # Frameworks e linguagens (ex.: angular, react, ...)
├── cloud/           # Provedores e infra (ex.: cloudflare, aws, ...)
└── observability/   # Telemetria, logs, métricas, tracing e SLOs
```

## Adaptadores disponíveis

| Categoria | ID | O que entrega |
| --- | --- | --- |
| `stack` | [`angular`](stacks/angular/conventions.md) | Convenções Angular modernas (standalone, Signals, `OnPush`, `inject()`, Vitest, Playwright), checks para `phase-code-review` e preset de editor |
| `stack` | [`react`](stacks/react/conventions.md) | Convenções React modernas (componentes funcionais, Hooks, estado cliente/servidor, RSC, testes de componente/E2E e TypeScript quando configurado), checks para `phase-code-review` e preset de editor |

> Próximos adaptadores previstos no roadmap: `cloud/cloudflare`, `cloud/aws` e `observability/`.

## Contrato de um adaptador

Cada adaptador vive em `adapters/<categoria_dir>/<id>/` (onde `<categoria_dir>` é `stacks`, `cloud` ou `observability`) e deve conter um manifesto `adapter.json` válido, verificado automaticamente por [`scripts/validate-kit.py`](../scripts/validate-kit.py):

```json
{
  "id": "angular",
  "name": "Angular",
  "category": "stack",
  "version": "1.0.0",
  "description": "Resumo curto do escopo do adaptador.",
  "detect": {
    "files": ["angular.json"],
    "packages": ["@angular/core", "@angular/cli"]
  },
  "commands": {
    "lint": "yarn lint",
    "typecheck": "npx tsc --noEmit",
    "test": "yarn ng test --watch=false",
    "e2e": "npx playwright test --reporter=list"
  },
  "files": {
    "conventions": "conventions.md",
    "review_checks": "review-checks.md",
    "editor_settings": "editor-settings.json"
  }
}
```

### Campos do `adapter.json`

- **`id`** *(obrigatório)*: identificador kebab-case (`^[a-z0-9][a-z0-9-]*$`), idêntico ao nome do diretório.
- **`name`** *(obrigatório)*: nome legível do adaptador.
- **`category`** *(obrigatório)*: `"stack"` (em `adapters/stacks/`), `"cloud"` (em `adapters/cloud/`) ou `"observability"` (em `adapters/observability/`).
- **`version`** *(opcional)*: versão semântica do adaptador (ex.: `"1.0.0"`).
- **`description`** *(obrigatório)*: descrição concisa de quando aplicar o adaptador.
- **`detect`** *(obrigatório)*: objeto com pelo menos uma lista não vazia entre `files`, `packages` ou `directories` — usado por `simbiose`/`integrar` para sugerir o acoplamento automaticamente.
- **`commands`** *(opcional)*: comandos sugeridos para preencher `<LINT_CMD>`, `<TYPECHECK_CMD>`, `<TEST_CMD>`, `<E2E_CMD>`, `<BUILD_CMD>` ou `<DEV_CMD>` quando não detectados diretamente no projeto.
- **`files`** *(obrigatório)*: caminhos relativos dentro do diretório do adaptador (os nomes de arquivo podem ser personalizados desde que respeitem o manifesto e permaneçam dentro da pasta do adaptador):
  - `conventions` *(obrigatório)*: convenções de código, arquitetura e testes a compor em `.claude/PROJECT_REFERENCE.md` e `AGENTS.md`.
  - `review_checks` *(obrigatório)*: checklist específico carregado em [`processes/phase-code-review.md`](../processes/phase-code-review.md) (§2–§4) a partir do caminho declarado em `adapter.json`.
  - `editor_settings` *(opcional)*: JSON com preferências de editor/formatador específicas da stack (no caminho declarado em `files.editor_settings`) para mesclar em `.cursor/settings.json` mediante aprovação.
  - `skills` *(opcional)*: lista de subdiretórios relativos contendo `SKILL.md` com frontmatter válido (`name` e `description`). Quando o adaptador é acoplado, cada skill é instalada seguindo a convenção de fonte única de verdade do kit: o corpo vira canônico em `processes/<name>.md` e os wrappers finos correspondentes (`.agents/skills/<name>/SKILL.md`, `.claude/skills/<name>/SKILL.md`, `.cursor/rules/<name>.mdc`, `AGENTS.md`, `.github/copilot-instructions.md`) apontam para ele.

## Como o acoplamento funciona

1. **Detecção (`simbiose` / `integrar`):** inspeciona o projeto host usando os sinais de `detect` nos `adapters/*/*/adapter.json` disponíveis (ou a escolha explícita do usuário em projetos novos).
2. **Plano com confirmação e checagem de colisões:** apresenta quais adaptadores serão acoplados, os caminhos declarados em cada `adapter.json` (`files.conventions`, `files.review_checks`, `files.editor_settings` e `files.skills`) e verifica se há colisão de nomes entre skills dos adaptadores selecionados ou com processos já existentes em `processes/<name>.md`. Havendo colisão, apresenta o conflito no plano e preserva os arquivos existentes até a decisão do usuário.
3. **Instalação seletiva:** copia apenas os adaptadores aprovados para `adapters/` do projeto host (sem levar adaptadores de outras stacks), compõe o arquivo declarado em `files.conventions` em `.claude/PROJECT_REFERENCE.md`, referencia o arquivo declarado em `files.review_checks` no fluxo de revisão, mescla `files.editor_settings` apenas quando presente e aprovado e, quando houver `files.skills`, instala apenas as skills aprovadas como canônicos em `processes/<name>.md` com seus respectivos wrappers finos nas ferramentas ativas (se o usuário optar por pular uma skill colidente mantendo ambos os adaptadores em `adapters/`, os dois adaptadores permanecem válidos e apenas a skill selecionada entra em `processes/`).
