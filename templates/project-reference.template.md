# <PROJECT_NAME> - Referência do Projeto

> **TEMPLATE** — preencha os marcadores `<...>` e `(preencha: ...)` com os dados do seu projeto.
> **LEIA ESTE ARQUIVO NO INÍCIO DE CADA SESSÃO DE DESENVOLVIMENTO** (humano ou AI).
> Overview alto-nível da arquitetura, stack, padrões e convenções do projeto.
> Complementado por [`docs/discovery.md`](../docs/discovery.md) (snapshot file-level do codebase; também é um modelo a preencher pelo projeto).

---

## Regras Críticas

1. Sempre leia este arquivo antes de iniciar qualquer tarefa.
2. Respeite a arquitetura e os padrões existentes descritos abaixo.

---

## Visão Geral do Projeto

- **Nome:** <PROJECT_NAME>
- **Tipo:** (preencha: tipo da aplicação, ex: aplicação administrativa interna)
- **Idioma da UI:** (preencha: idioma da interface, ex: Português brasileiro (pt-BR) — todo texto hardcoded)
- **Empresa/Time:** (preencha: nome do time ou organização)
- **Propósito:** (preencha: o que a aplicação faz)
- **Público-alvo:** (preencha: quem usa a aplicação)

---

## Stack Tecnológico

| Camada                  | Tecnologia                                          |
| ----------------------- | --------------------------------------------------- |
| Framework               | Angular (preencha: versão) (standalone components)  |
| Biblioteca UI           | Angular Material (preencha: versão)                 |
| Estilização             | SCSS (padrão de arquitetura 7-1)                    |
| Gerenciamento de Estado | Angular Signals (sem NgRx/Redux)                    |
| Formulários             | Angular Reactive Forms + validação com Zod (preencha: versão) |
| HTTP                    | Angular HttpClient com RxJS (preencha: versão)      |
| Autenticação            | (preencha: ex: OAuth2 / Keycloak (JWT em cookies))  |
| Ícones                  | (preencha: biblioteca de ícones) + `MatIcon`        |
| Manipulação de Datas    | (preencha: ex: date-fns versão)                     |
| Editor de Código        | (preencha: ex: CodeMirror, ou remover se N/A)       |
| TypeScript              | (preencha: versão) (modo strict)                    |
| Gerenciador de Pacotes  | (preencha: ex: Yarn 1.22 / pnpm / npm)              |
| Testes Unitários        | Vitest (preencha: versão) (`@angular/build:unit-test`) |
| Testes E2E              | Playwright (preencha: versão)                       |
| Linting                 | ESLint (preencha: versão) + Prettier (preencha: versão) |
| Template Base           | (preencha: template base, ou remover se N/A)        |
| Node.js                 | (preencha: versão LTS)                              |

---

## Estrutura do Projeto

```
<PROJECT_KEY>/
├── <APP_DIR>/                   # Aplicação Angular principal
│   ├── src/
│   │   ├── app/
│   │   │   ├── modules/         # Módulos de feature (Clean Architecture)
│   │   │   │   ├── authentication/   # (preencha: liste seus módulos de feature)
│   │   │   │   ├── authorization/
│   │   │   │   ├── home/
│   │   │   │   └── <feature>/
│   │   │   └── shared/          # Código compartilhado (erros, mensagens, UI, utils)
│   │   ├── assets/              # Assets estáticos & SCSS (padrão 7-1)
│   │   ├── environments/        # Configs de ambiente (local, dev, staging, prod, test)
│   │   └── main.ts              # Ponto de entrada (standalone bootstrap)
│   ├── server/                  # Mock server Express para desenvolvimento local
│   │   ├── main.ts              # Servidor Express na porta 3000
│   │   └── modules/             # Rotas mock por feature
│   │       ├── authentication.routes.ts   # (preencha: uma rota mock por módulo)
│   │       └── <feature>.routes.ts
│   ├── angular.json             # Configuração do workspace Angular CLI
│   ├── vitest.config.ts         # Configuração do Vitest
│   ├── package.json             # Dependências & scripts
│   └── tsconfig.json            # Configuração TypeScript (strict)
├── .github/workflows/           # CI/CD (testes, deploy) — (preencha conforme seu CI)
├── infra/                       # Configs IaC por ambiente (se aplicável)
├── Dockerfile                   # Multi-stage (preencha: ex: Node build -> Nginx Alpine)
├── cloudbuild.yaml              # (preencha: ex: build pipeline do cloud provider)
├── Makefile                     # Automação de build/deploy
├── main.tf / provider.tf        # IaC (preencha: ex: Terraform)
└── variables.tf
```

---

## Arquitetura: Clean Architecture + Gateway Pattern

Cada módulo de feature segue esta estrutura de camadas rigorosa:

```
modules/<feature>/
├── domain/      # Entidades, interfaces de gateway, use cases, repositórios
├── infra/       # Implementações HTTP de gateway, DTOs, mappers
├── main/        # Fachadas de implementação
└── view/        # Componentes, rotas, guards
```

**Princípios-chave:**

- A camada **domain** define interfaces de gateway e use cases (lógica de negócio)
- A camada **infra** implementa gateways HTTP, DTOs e mappers
- A camada **view** contém componentes Angular, rotas e guards
- Sem store de estado global — estado é local com Angular Signals

---

## Módulos de Feature Existentes

> (preencha: liste os módulos do seu projeto. Os módulos `authentication`/`authorization`/`home`
> são comuns; adicione os seus de feature.)

| Módulo              | Rota                | Propósito                                                          |
| ------------------- | ------------------- | ------------------------------------------------------------------ |
| authentication      | `/authentication`   | Fluxo de login (preencha: provider, ex: OAuth2/Keycloak)          |
| authorization       | `/authorization`    | RBAC, página de não autorizado                                     |
| home                | `/home`             | Dashboard/página inicial                                           |
| <feature>           | `/<feature>`        | (preencha: propósito do módulo)                                    |

Todas as rotas são **lazy-loaded** via `loadChildren` em `app.routes.ts`.

---

## Autenticação e Autorização

> (preencha: descreva o fluxo de autenticação do seu projeto. Exemplo abaixo.)

- **Fluxo:** OAuth2 Authorization Code com PKCE (ex.: Keycloak)
- **Tokens:** JWT armazenado em cookies (`ngx-cookie-service`)
- **Login:** Duas etapas — redireciona para Keycloak, depois troca código por token
- **Interceptors:**
  - `authInterceptor` — adiciona Bearer token
  - `unauthenticatedInterceptor` — trata 401, redireciona para login
  - `forbiddenInterceptor` — trata 403
- **Guards:**
  - `authGuard` — exige login
  - `authorizationGuard` — verifica `data.roles` nas rotas
- **Roles (padrão de nomeação):** `<feature>-view`, `<feature>-manager`, `<feature>-<ação>` (preencha: liste as roles do seu projeto seguindo o padrão `[módulo]-[contexto]-[ação]`)

---

## Código Compartilhado (`src/app/shared/`)

> (preencha: liste as pastas compartilhadas do seu projeto. Exemplo abaixo.)

| Diretório          | Propósito                                                            |
| ------------------ | -------------------------------------------------------------------- |
| `errors/`          | Tratamento de erros — Strategy pattern (Zod, HTTP, Native, Fallback) |
| `messages/`        | Mensagens snackbar — Strategy pattern (Sucesso, Erro, Info, Aviso)   |
| `services/`        | ThemeService (light/dark), tradução do paginator para pt-BR          |
| `ui/components/`   | confirmation-dialog, loading, page-header                            |
| `ui/layouts/`      | Full layout (sidebar + header), blank layout                         |
| `ui/pipes/`        | Pipes de formatação compartilhados                                   |
| `utils/`           | Helpers de query params HTTP, paginação, mappers                     |
| `utils/constants/` | Constantes compartilhadas                                            |

---

## Padrões e Convenções de Código

1. **Standalone components** em todos os lugares (Angular moderno, sem NgModules para features)
2. **Função `inject()`** para DI (não injeção por construtor)
3. **Angular Signals** (`signal()`, `computed()`, `effect()`) para estado reativo
4. **`takeUntilDestroyed`** para limpeza de subscriptions
5. **`ChangeDetectionStrategy.OnPush`** onde aplicável (preferir Zoneless para módulos novos)
6. **Zod** em conjunto com Angular Validators para validação de schema
7. **ControlValueAccessor** para controles de formulário customizados
8. **Strategy pattern** para tratamento de erros e exibição de mensagens
9. **Seletores:** Componentes usam prefixo `app-` (kebab-case), diretivas usam `app` (camelCase)
10. **Sem Storybook**, sem arquivos de tradução i18n, sem biblioteca de estado global

---

## Estilização

- **Padrão SCSS 7-1:** abstracts, base, components, layout, pages, themes, utilities, vendors
- **Temas:** (preencha: lista de temas, ex: default, blue, orange, ... com modo light/dark)
- **CSS custom properties** para Material Design tokens
- **Fonte:** (preencha: ex: Inter (Google Fonts))
- **Prettier:** (preencha: largura, ex: 120 caracteres — `printWidth: 120`)

---

## Mock Server (Desenvolvimento Local)

O projeto possui um **servidor Express** em `<APP_DIR>/server/` que fornece dados mockados para desenvolvimento local.

- **Porta:** 3000
- **Executado via:** `yarn local` (inicia Angular + mock server simultaneamente)
- **Estrutura:** Uma rota por módulo em `server/modules/`
- **Dependências:** Express, cors, `@faker-js/faker` para geração de dados

Rotas registradas (preencha conforme os módulos do seu projeto):

```typescript
app.use('/<auth-base>', authRoutes);
app.use('/<feature-base>', <feature>Routes);
// ... uma linha por módulo de feature
```

> Ao adicionar uma nova feature, registrar suas rotas mock neste servidor (uma rota por módulo em `server/modules/`).

---

## Configurações de Build

| Config      | Base Href              | Propósito          |
| ----------- | ---------------------- | ------------------ |
| production  | `/`                    | Deploy em produção |
| staging     | `/<PROJECT_KEY>/` | Staging/UAT        |
| development | `/<PROJECT_KEY>/` | Ambiente de dev    |
| local       | `/<PROJECT_KEY>/` | Dev local (padrão) |
| test        | `/<PROJECT_KEY>/` | Ambiente de teste  |

---

## Scripts Principais

| Script                  | Descrição                               |
| ----------------------- | --------------------------------------- |
| `yarn start`            | Dev server (config local)               |
| `yarn local`            | Dev server + mock Express server        |
| `yarn dev`              | Dev server (config development)         |
| `yarn build-production` | Build otimizado para produção           |
| `yarn build-staging`    | Build para staging                      |
| `yarn ng test`          | Testes unitários com cobertura (Vitest) |
| `yarn test:dev`         | Testes unitários em modo watch          |
| `yarn lint`             | ESLint                                  |
| `yarn format`           | Prettier                                |
| `yarn analyze`          | Análise de bundle (esbuild-visualizer)  |

---

## Configuração de Ambiente

```typescript
{
  production: boolean;
  apiBaseUrl: string; // ex: 'http://localhost:3000' em local
  // (preencha: URLs de outros serviços e limites configuráveis por ambiente, se houver)
  auth: {
    issuerUrl: string; // URL do provedor OAuth2/OIDC (ex: realm do Keycloak)
    clientId: string; // (preencha: client id público do seu app)
    redirectUri: string;
  }
}
```

> **Segredos fora do front-end:** numa SPA, use OAuth2 Authorization Code com PKCE e um client público. Não coloque `client_secret` nem outro segredo na configuração de ambiente do front-end, porque tudo o que vai para o bundle fica visível para quem abre o app.

---

## Testes

- **Unitários:** (preencha: nº aproximado) arquivos `.spec.ts`, Vitest com `@angular/build:unit-test`
- **Configuração:** `vitest.config.ts` na raiz do app
- **Setup:** `src/test-setup.ts` (configurado automaticamente pelo builder)
- **Thresholds de cobertura (alvo):** (preencha: ex: 80% statements/branches/functions/lines)
- **E2E:** Playwright (ver `docs/e2e.md` para convenções).
- **Padrões:** TestBed, `vi.fn()` / `vi.mock()` (Vitest nativo), `MockedObject` (tipo do Vitest), `spyOn` (Jasmine-compatible via globals)

> **IMPORTANTE:** Não modificar `vitest.config.ts` ou `test-setup.ts`. Não adicionar `TestBed.initTestEnvironment()` nos arquivos spec — o builder já cuida disso.

---

## CI/CD e Infraestrutura

> (preencha: descreva o CI/CD do seu projeto. Exemplo abaixo.)

- **CI (ex: GitHub Actions):**
  - `tests.yml` — testes em PRs para os branches principais
  - `deploy.yml` — deploy em push (preencha: regiões/ambientes)
  - `gmud.yml` — documentos de gestão de mudança em merge de PR (se aplicável)
- **Docker:** Multi-stage (preencha: ex: Node build → Nginx Alpine), porta (preencha)
- **Build/Registry:** (preencha: ex: Cloud Build, push para o container registry)
- **IaC:** (preencha: ex: Terraform — infraestrutura cloud)
- **Makefile:** `make build`, `make push`, `make deploy`

---

## Backend (BFF)

> (preencha: descreva o backend que o frontend consome. Exemplo de padrão BFF abaixo.)

O frontend se comunica com um **BFF (Backend for Frontend)** (preencha: linguagem/framework, ex: Python/FastAPI), que proxia requisições para os serviços internos do time.

**Repositório:** `<OTHER_PROJECT>` (preencha: repositório do backend)

**Arquitetura de comunicação:**

```
Angular Frontend  →  BFF (preencha: framework)  →  Serviços internos (APIs privadas)
   HttpClient          (preencha: runtime)          (preencha: orquestração)
```

**Endpoints específicos por feature** são documentados na spec da própria feature (ver `templates/spec-template.md`).

---

## Guia: Adicionando um Novo Módulo de Feature

1. Criar o módulo em `<APP_DIR>/src/app/modules/<nome-da-feature>/`
2. Seguir Clean Architecture: `domain/`, `infra/`, `main/`, `view/`
3. Definir interfaces de gateway em `domain/gateways/`
4. Implementar gateways HTTP em `infra/gateways/` com DTOs e mappers
5. Criar use cases em `domain/use-cases/`
6. Adicionar rotas lazy-loaded em `view/` e registrar em `app.routes.ts`
7. Usar standalone components com `inject()`, Signals e OnPush
8. Proteger rotas com `authorizationGuard` e roles apropriadas
9. Escrever testes unitários (`.spec.ts`) para use cases, mappers e componentes
10. Todo texto de UI deve estar em Português (pt-BR)
11. Adicionar mocks no mock server (`server/modules/`) para desenvolvimento local
