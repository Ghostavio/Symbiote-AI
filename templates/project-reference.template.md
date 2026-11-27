# <PROJECT_NAME> - Referência do Projeto

> **TEMPLATE** — preencha os marcadores `<...>` e `(preencha: ...)` com os dados do seu projeto.
> **LEIA ESTE ARQUIVO NO INÍCIO DE CADA SESSÃO DE DESENVOLVIMENTO** (humano ou AI).
> Overview alto-nível da arquitetura, stack, padrões e convenções do projeto.
> Complementado por [`docs/discovery.md`](../docs/discovery.md) (snapshot file-level do codebase; também é um modelo a preencher pelo projeto).
> Se o projeto acoplou adaptadores em `adapters/` via `simbiose` (ex.: `adapters/stacks/angular/`), componha aqui as convenções declaradas em `files.conventions` de cada adaptador ativo.

---

## Regras Críticas

1. Sempre leia este arquivo antes de iniciar qualquer tarefa.
2. Respeite a arquitetura e os padrões existentes descritos abaixo.

---

## Visão Geral do Projeto

- **Nome:** <PROJECT_NAME>
- **Tipo:** (preencha: tipo da aplicação, ex.: aplicação web interna, API REST, CLI, monorepo)
- **Idioma da UI:** (preencha: idioma da interface, ex.: Português brasileiro (pt-BR) — todo texto hardcoded)
- **Empresa/Time:** (preencha: nome do time ou organização)
- **Propósito:** (preencha: o que a aplicação faz)
- **Público-alvo:** (preencha: quem usa a aplicação)

---

## Stack Tecnológico

| Camada                  | Tecnologia                                                               |
| ----------------------- | ------------------------------------------------------------------------ |
| Linguagem / Runtime     | (preencha: ex.: TypeScript / Node.js LTS, Python 3.12, Go 1.23, .NET 9)  |
| Framework principal     | (preencha: framework e versão)                                           |
| Biblioteca UI / Estilos | (preencha: design system / CSS / tokens, ou N/A para backend/CLI)        |
| Gerenciamento de Estado | (preencha: estratégia de estado local/remoto, ou N/A)                    |
| Validação / Schemas     | (preencha: ex.: Zod, Pydantic, Bean Validation, FluentValidation)        |
| Cliente HTTP / API      | (preencha: biblioteca HTTP / contratos de API)                           |
| Autenticação            | (preencha: ex.: OAuth2/OIDC com PKCE, JWT, sessão, API key)              |
| Gerenciador de Pacotes  | (preencha: ex.: pnpm, yarn, npm, uv, maven, go mod, dotnet)              |
| Testes Unitários        | (preencha: runner e versão — comando `<TEST_CMD>`)                       |
| Testes E2E / Integração | (preencha: ex.: Playwright, Cypress, supertest, pytest — `<E2E_CMD>`)    |
| Linting / Formatação    | (preencha: linter + formatador — comando `<LINT_CMD>`)                   |
| Adaptadores acoplados   | (preencha: lista de adaptadores ativos em `adapters/`, ou "nenhum")      |

---

## Estrutura do Projeto

```text
<PROJECT_KEY>/
├── <APP_DIR>/                   # Aplicação principal (ou raiz do repo)
│   ├── <src>/
│   │   ├── modules/             # Módulos de feature (ou pacotes por domínio)
│   │   │   ├── authentication/  # (preencha: liste seus módulos de feature)
│   │   │   ├── authorization/
│   │   │   └── <feature>/
│   │   └── shared/              # Código compartilhado (erros, mensagens, UI, utils)
│   ├── <e2e-dir>/               # Testes E2E / integração (se aplicável)
│   └── <manifesto-da-stack>     # package.json / pyproject.toml / go.mod / *.csproj / pom.xml
├── .github/workflows/           # CI/CD (testes, lint, deploy) — (preencha conforme seu CI)
├── infra/                       # Configs IaC por ambiente (se aplicável)
└── Dockerfile                   # (preencha ou remova se N/A)
```

---

## Arquitetura e Camadas

Descreva a arquitetura adotada no projeto (exemplo abaixo em camadas / Clean Architecture — ajuste à convenção real do repositório):

```text
modules/<feature>/
├── domain/          # Entidades, contratos/interfaces de gateway, use cases
├── infra/           # Implementações HTTP/banco, DTOs, mappers
├── application/     # Orquestração / fachadas (ou main/)
└── presentation/    # Interface, rotas, controllers, guards (ou view/)
```

**Princípios-chave:**

- A camada **domain** concentra regras de negócio puras e interfaces (sem detalhes de transporte/UI).
- A camada **infra** encapsula integrações externas (HTTP, banco, filas), DTOs e mappers.
- A camada **presentation/API** lida com entrada/saída, rotas e controle de acesso.
- Mantenha nomes e tipos coerentes entre todas as camadas.

---

## Módulos de Feature Existentes

> (preencha: liste os módulos/serviços existentes do seu projeto.)

| Módulo         | Rota / Entry point | Propósito                                                    |
| -------------- | ------------------ | ------------------------------------------------------------ |
| authentication | `/authentication`  | Fluxo de autenticação (preencha: provedor OAuth2/OIDC/outro) |
| authorization  | `/authorization`   | RBAC / controle de permissões                                |
| home           | `/home`            | Página inicial / dashboard (ou health/root em APIs)          |
| `<feature>`    | `/<feature>`       | (preencha: propósito do módulo)                              |

---

## Autenticação e Autorização

> (preencha: descreva o fluxo de autenticação/autorização do seu projeto. Exemplo abaixo.)

- **Fluxo:** (preencha: ex.: OAuth2 Authorization Code com PKCE via provedor OIDC)
- **Tokens / Sessão:** (preencha: ex.: cookies HttpOnly, header `Authorization: Bearer`)
- **Interceptors / Middlewares:**
  - autenticação (anexa credencial ou valida sessão)
  - tratamento de `401` (não autenticado) e `403` (sem permissão)
- **Guards / Políticas:** proteção de rotas/endpoints por papel ou escopo
- **Roles (padrão de nomeação):** `<feature>-view`, `<feature>-manager`, `<feature>-<ação>` (ajuste ao padrão do time)

---

## Código Compartilhado (`<src>/shared/`)

> (preencha: liste as pastas compartilhadas do seu projeto.)

| Diretório  | Propósito                                               |
| ---------- | ------------------------------------------------------- |
| `errors/`  | Tratamento padronizado de erros (validação, HTTP, etc.) |
| `ui/`      | Componentes reutilizáveis, layouts, feedback visual     |
| `utils/`   | Helpers de paginação, formatação, mappers e constantes  |

---

## Padrões e Convenções de Código

> Se o projeto acoplou um adaptador de stack em `adapters/` (ex.: `adapters/stacks/angular/`), importe ou referencie aqui as regras de `files.conventions` desse adaptador e complemente com convenções específicas do time.

1. **Idioma da UI e mensagens:** (preencha: padrão pt-BR com acentuação correta)
2. **Estilo e tipagem:** (preencha: ex.: modo strict, sem `any` desnecessário, funções pequenas e puras)
3. **Injeção de dependências e ciclo de vida:** (preencha: padrão da stack para DI e limpeza de recursos)
4. **Validação de dados:** (preencha: biblioteca de schemas/validadores)
5. **Tratamento de erros e logs:** (preencha: estratégia de erros, logs estruturados sem dados sensíveis)
6. **Convenções de nomeação:** (preencha: arquivos, símbolos, rotas, seletores `data-testid`)

---

## Estilização e Acessibilidade *(quando aplicável a UI)*

- **Arquitetura de estilos / tokens:** (preencha: CSS variables, Tailwind, SCSS, design tokens)
- **Temas:** (preencha: suporte a light/dark mode, se aplicável)
- **Acessibilidade:** `aria-label` em controles interativos, navegação por teclado e contraste adequado
- **Formatação:** (preencha: ex.: Prettier/Biome/Black/gofmt e largura de linha)

---

## Mock Server / Desenvolvimento Local *(quando aplicável)*

Descreva como a aplicação roda localmente sem depender de todos os serviços externos:

- **Comando local:** `<DEV_CMD>` (disponível em `<DEV_URL>`)
- **Mocks / Fixtures:** (preencha: localização de rotas mock, MSW, fixtures ou seed local)
- **Regra:** dados mock devem passar pelos validadores reais implementados no projeto (CPF/CNPJ, email, telefone, etc.).

---

## Scripts e Comandos Principais

| Comando           | Descrição                                  |
| ----------------- | ------------------------------------------ |
| `<DEV_CMD>`       | Inicia ambiente de desenvolvimento local   |
| `<BUILD_CMD>`     | Build da aplicação                         |
| `<TEST_CMD>`      | Testes unitários                           |
| `<E2E_CMD>`       | Testes E2E / integração (quando aplicável) |
| `<LINT_CMD>`      | Lint e análise estática local              |
| `<TYPECHECK_CMD>` | Verificação de tipos (quando aplicável)    |

---

## Configuração de Ambiente

```text
# (preencha com as variáveis/chaves de configuração por ambiente)
APP_ENV=local
API_BASE_URL=<API_BASE_URL>   # URL da API/mock (ex.: http://localhost:3000 ou caminho relativo como /api quando houver proxy)
AUTH_ISSUER_URL=<URL do provedor OAuth2/OIDC>
AUTH_CLIENT_ID=<client id público>
```

> **Segredos fora do front-end e fora do git:** numa SPA/front-end, use OAuth2 Authorization Code com PKCE e um client público. Não coloque `client_secret` nem outro segredo na configuração de ambiente do front-end, porque tudo o que vai para o bundle fica visível para quem abre o app. Em backends/CLIs, leia segredos apenas de variáveis de ambiente ou secret managers.

---

## Testes

- **Unitários:** `<TEST_CMD>` — (preencha: framework, padrão de arquivos e regras específicas da stack/adaptador)
- **Cobertura alvo:** (preencha: ex.: 80% statements/branches/functions/lines)
- **E2E:** `<E2E_CMD>` — ver [`docs/e2e.md`](../docs/e2e.md) para convenções de Page Object Model e `data-testid` (quando aplicável)
- **Isolamento:** evite rodar múltiplas instâncias concorrentes do runner de testes quando compartilharem portas, banco ou cache.

---

## CI/CD e Infraestrutura

> (preencha: descreva pipelines de CI/CD, deploy e infraestrutura do projeto.)

- **CI:** (preencha: GitHub Actions / Azure Pipelines / GitLab CI — checks obrigatórios em PR)
- **Deploy / Runtime:** (preencha: containers, serverless, Workers, Kubernetes, etc.)
- **IaC:** (preencha: Terraform / CDK / Pulumi / Wrangler, ou N/A)

---

## Board e Fluxo de Trabalho

- **Tracker e board:** (preencha: ferramenta, URL e conector, ou nenhum)
- **Tipos e vínculos:** (preencha: como o time representa iniciativas, entregas, tarefas e bugs)
- **Critérios de aceite:** (preencha: campo, seção da descrição ou template usado por tipo de item)
- **Estados e transições:** (preencha: etapa inicial, início do trabalho, revisão e conclusão)
- **Responsáveis pelas transições:** (preencha: agente, automação ou pessoa, incluindo condições para concluir)

---

## Integrações e Serviços Relacionados

> (preencha: descreva APIs, BFFs ou serviços consumidos/expostos pelo projeto.)

- **Repositórios relacionados:** `<OTHER_PROJECT>` (preencha ou remova se N/A)
- **Fluxo de comunicação:**

```text
Cliente / Frontend  →  BFF / API Gateway (preencha)  →  Serviços internos / Banco
```

**Endpoints específicos por feature** são documentados na spec da própria feature (ver `templates/spec-template.md`).

---

## Guia: Adicionando um Novo Módulo de Feature

1. Crie o módulo em `<src>/modules/<nome-da-feature>/` (ou na convenção de pastas do projeto).
2. Respeite a separação de camadas documentada acima (domínio desacoplado de infra/UI).
3. Defina contratos/interfaces e implemente gateways/adaptadores com DTOs e mappers.
4. Registre rotas/endpoints e proteja com as políticas/permissões da spec.
5. Siga as convenções da stack (e do adaptador ativo em `adapters/`, quando houver).
6. Escreva testes unitários (e E2E quando aplicável) cobrindo casos felizes, erros e bordas.
7. Garanta textos de UI no idioma configurado (padrão pt-BR) e atualize mocks locais quando aplicável.
