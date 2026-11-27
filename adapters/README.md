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

> Próximos adaptadores previstos no roadmap: `stacks/react`, `cloud/cloudflare`, `cloud/aws` e `observability/`.

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
- **`files`** *(obrigatório)*: caminhos relativos dentro do diretório do adaptador:
  - `conventions` *(obrigatório)*: convenções de código, arquitetura e testes a compor em `.claude/PROJECT_REFERENCE.md` e `AGENTS.md`.
  - `review_checks` *(obrigatório)*: checklist específico carregado em [`processes/phase-code-review.md`](../processes/phase-code-review.md) (§2–§4).
  - `editor_settings` *(opcional)*: JSON com preferências de editor/formatador específicas da stack para mesclar em `.cursor/settings.json` mediante aprovação.
  - `skills` *(opcional)*: lista de subdiretórios relativos contendo `SKILL.md` com frontmatter válido, instalados nos wrappers apenas quando o adaptador é acoplado.

## Como o acoplamento funciona

1. **Detecção (`simbiose` / `integrar`):** inspeciona o projeto host usando os sinais de `detect` nos `adapters/*/*/adapter.json` disponíveis (ou a escolha explícita do usuário em projetos novos).
2. **Plano com confirmação:** apresenta quais adaptadores serão acoplados, quais comandos e convenções entram no projeto e se há presets de editor ou skills opcionais a incluir.
3. **Instalação seletiva:** copia apenas os adaptadores aprovados para `adapters/` do projeto host (sem levar adaptadores de outras stacks), compõe as convenções em `.claude/PROJECT_REFERENCE.md` e referencia `review-checks.md` no fluxo de revisão.
