# Especificacao: [Nome da Feature]

<!-- Preencha os metadados abaixo. Exemplo:
> **Fonte:** Reunião de alinhamento - DD/MM/AAAA (link para documento/transcrição)
> **Participantes:** Nome Completo (Papel), Nome Completo (Papel)
> **Status:** Rascunho | Em revisão | Pronto para implementação
> **Referência técnica do projeto:** [`project-reference.template.md`](/templates/project-reference.template.md)
> **Azure DevOps Feature ID:** #XXXXX (ID do Feature no Board — usado para sincronização automática de work items via Azure MCP)
-->

> **Fonte:** [link ou descrição da origem dos requisitos]
> **Participantes:** [lista de participantes com papéis]
> **Status:** Rascunho
> **Referência técnica do projeto:** [`project-reference.template.md`](/templates/project-reference.template.md)
> **Azure DevOps Feature ID:** [ID do Feature no Azure DevOps, ex: #XXXXX — usado para sincronização automática de work items via Azure MCP. Deixar em branco se não houver integração com Board]

---

## 1. Visao Geral da Feature

<!-- Descreva o escopo da feature em 2-3 parágrafos. Inclua:
- O que a feature faz (capacidade adicionada ao app)
- Quantas telas compõem a feature e seus nomes
- Se o escopo é frontend-only ou inclui backend
- Qualquer decisão de escopo importante (ex: "apenas frontend, endpoints como referência para mocks")

Exemplo:
> **Escopo desta implementação:** Este documento especifica exclusivamente o **frontend** (Angular). Nenhuma implementação de backend faz parte deste escopo.

A feature **[Nome]** adiciona ao app a capacidade de [descrição]. É composta por **N telas** principais:
1. **[Tela A]** — descrição curta
2. **[Tela B]** — descrição curta
-->

> **Escopo desta implementação:** [frontend-only / full-stack / outro]

A feature **[Nome da Feature]** adiciona ao app a capacidade de [descrição da capacidade]. É composta por **[N] telas** principais:

1. **[Nome da Tela 1]** -- [descrição curta]
2. **[Nome da Tela 2]** -- [descrição curta]

### Navegacao no Menu Lateral (Sidebar)

<!-- Descreva onde a feature aparece no menu lateral. Inclua:
- Nome da nova seção (se aplicável) ou seção existente
- Itens de menu com ícone, rota e descrição
- Se alguma tela NÃO possui item no menu (ex: acessada via botão em outra tela)

Exemplo: A tela de Detalhes não possui item próprio no menu — é acessada exclusivamente via botão "Visualizar" nos resultados da busca.
-->

Nova seção **[NOME DA SEÇÃO]** no menu lateral com o(s) item(ns):

| Item | Icone | Rota | Descricao |
| ---- | ----- | ---- | --------- |
|      |       |      |           |

### Fluxo de Navegacao

<!-- Descreva o fluxo entre as telas usando um diagrama ASCII. Inclua:
- Ponto de entrada (sidebar ou outra tela)
- Cada tela com sua rota
- Ações que levam de uma tela para outra
- Breadcrumbs de cada tela

Exemplo:
```
Sidebar: PEDIDOS > Buscar
        |
        v
[Tela: Busca de Pedidos]  (/orders)
        |
        v  (clica "Visualizar" em um resultado)
[Tela: Detalhes do Pedido]  (/orders/:id)
   Breadcrumb: PEDIDOS > DETALHES DO PEDIDO
```
-->

```
[Diagrama de fluxo aqui]
```

---

## 2. Tela: [Nome da Tela]

<!-- REPITA esta seção inteira (2.x) para CADA tela da feature.
Cada tela deve conter todas as subseções abaixo. -->

### 2.1 Layout Geral

<!-- Descreva os elementos visuais fixos da tela:
- Título exibido no topo
- Subtítulo (se houver)
- Ícone representativo
- Se possui breadcrumb ou não
- Áreas principais da tela (ex: "área superior sempre visível + área inferior com abas")
-->

- **Título:** "[Título da tela]"
- **Subtítulo:** "[Subtítulo ou descrição curta]"
- **Icone:** [nome do ícone]
- **Breadcrumb:** [breadcrumb ou "Sem breadcrumb (tela raiz)"]

### 2.2 Formularios e Campos

<!-- Liste TODOS os campos de formulário da tela em tabela. Inclua:
- Nome do campo e placeholder
- Tipo do campo (texto, email, select, date, textarea, etc.)
- Máscara (se aplicável): ex: `000.000.000-00` para CPF
- Validações: obrigatório, formato, tamanho mínimo/máximo
- Regra de máscara dinâmica (ex: CPF ou CNPJ baseado no número de caracteres)

Se a tela não possui formulário, remova esta subseção.
-->

| Campo | Placeholder | Tipo | Mascara | Validacao |
| ----- | ----------- | ---- | ------- | --------- |
|       |             |      |         |           |

### 2.3 Botoes e Acoes

<!-- Liste todos os botões da tela com:
- Nome do botão
- Ícone (se houver)
- Ação executada ao clicar
- Condições de visibilidade (ex: "visível apenas se o operador possui role X")
- Cor ou estilo (se relevante: vermelho para destrutiva, verde para positiva, etc.)
-->

| Botao | Icone | Acao | Condicao de visibilidade |
| ----- | ----- | ---- | ------------------------ |
|       |       |      |                          |

### 2.4 Regras de Negocio

<!-- Descreva as regras de negócio ESPECÍFICAS desta tela:
- Regras de busca/filtro (ex: "busca por número do pedido retorna 1 resultado, por email do cliente pode retornar múltiplos")
- Regras de validação antes de submeter
- Regras de exibição condicional (ex: "campo X só aparece quando Y está preenchido")
- Formato de envio para API (ex: "apenas números, sem máscara")
- Comportamento ao pressionar Enter
- Qualquer decisão de produto documentada

Exemplo: "Mesmo com 1 resultado, o usuário deve visualizar o card e clicar 'Visualizar' — serve como confirmação para evitar acessar dados errados por digitação incorreta."
-->

- [Regra 1]
- [Regra 2]

### 2.5 Exibicao de Resultados / Dados

<!-- Descreva COMO os dados são exibidos na tela:
- Formato: tabela, carrossel de cards, lista, cards estáticos, etc.
- Campos exibidos em cada item (com exemplos concretos)
- Componente utilizado (ex: carrossel reutilizável, MatTable com paginação)
- Regras de paginação (local no frontend vs. server-side)
- Regras de ordenação

Para cards, use uma tabela detalhada:
| Elemento | Descrição | Exemplo |
| -------- | --------- | ------- |

Para tabelas, descreva as colunas:
| Coluna | Descrição | Tipo de dado | Exemplo |
| ------ | --------- | ------------ | ------- |
-->

| Elemento | Descricao | Exemplo |
| -------- | --------- | ------- |
|          |           |         |

### 2.6 Estados da Tela

<!-- Liste TODOS os estados possíveis da tela. Estados comuns:
- Inicial (antes de qualquer interação)
- Carregando (spinner/loading)
- Com resultados/dados
- Sem resultados (empty state com mensagem)
- Erro (mensagem de erro)
- Não carregado (para abas que carregam sob demanda)

Para cada estado, descreva o que é exibido visualmente.
-->

| Estado | Descricao |
| ------ | --------- |
|        |           |

### 2.7 Dialogs e Modais

<!-- Descreva todos os modais/dialogs que podem ser abertos a partir desta tela:
- Quando é aberto (qual botão/ação)
- Campos do modal (tabela com tipo, obrigatório/opcional)
- Fluxo do modal (passos: 1. exibe aviso, 2. preenche campos, 3. confirma, 4. feedback)
- Comportamento de sucesso e erro
- Avisos/warnings exibidos no modal

Se a tela não possui modais, remova esta subseção.
-->

#### Modal: [Nome do Modal]

**Trigger:** [quando é aberto]

| Campo | Tipo | Obrigatorio | Descricao |
| ----- | ---- | ----------- | --------- |
|       |      |             |           |

**Fluxo:**
1. [passo 1]
2. [passo 2]
3. [passo 3]

### 2.8 Subtelas / Telas Filhas

<!-- Descreva telas que são acessadas a partir desta tela (ex: telas de histórico acessadas a partir dos cards de resumo).
Para cada subtela, inclua:
- Rota
- Breadcrumb
- Layout e campos
- Filtros (se houver)
- Tabelas/dados exibidos

Se não houver subtelas, remova esta subseção.
-->

---

## 3. Componentes Reutilizaveis

<!-- Descreva componentes que serão compartilhados entre múltiplas telas ou contextos.
Para cada componente, inclua:
- Nome e propósito
- Contextos onde é utilizado (ex: "carrossel usado na busca e nas listas de itens relacionados")
- Comportamento detalhado (ex: quantidade de cards visíveis, setas de navegação, contador)
- Regras de responsividade (ex: "3 cards em telas normais, 2 em telas < 960px")
- Regras de paginação (local vs. server-side)

Exemplo: Carrossel horizontal reutilizável
- 3 cards por vez em telas normais, 2 em telas reduzidas
- Setas de navegação quando houver mais cards que o visível
- Contador: "EXIBINDO 3 DE 8"
- Paginação local no frontend (API chamada uma vez com page_size=100)
- Navegação por teclado: Tab entre cards, Enter para ação, setas para páginas
-->

### 3.1 [Nome do Componente]

**Uso:** [contextos onde é utilizado]

**Comportamento:**
- [regra 1]
- [regra 2]

---

## 4. Regras Gerais e Transversais

### 4.1 Logging (Auditoria)

<!-- Descreva a política de logging da feature:
- Quais ações geram log
- O que o log deve registrar (quem, o que, quando, sobre qual entidade)
- Se o log é gerado no frontend ou automaticamente pelo backend
- Quaisquer considerações de segurança

Exemplo: "Toda ação acionada por botão deve ser logada. O log é gerado automaticamente pelo backend ao acessar os endpoints."
-->

- [Política de logging]

### 4.2 Cores e Contraste

<!-- Descreva as regras de cores usadas na feature:
- Mapeamento de status para cores (tabela)
- Regras de fallback (ex: "qualquer status não mapeado = laranja")
- Considerações de dark mode
- Preferência por ícones outline vs. sólidos

Exemplo:
| Cor      | Status                    |
| -------- | ------------------------- |
| Verde    | ATIVO                     |
| Vermelho | INATIVO, BLOQUEADO        |
| Laranja  | Qualquer outro (fallback) |
-->

| Cor | Status / Uso |
| --- | ------------ |
|     |              |

### 4.3 Responsividade

<!-- Descreva a estratégia de responsividade:
- Desktop-first ou mobile-first
- Breakpoints relevantes (ex: 960px para tela dividida)
- Adaptações necessárias (ex: "carrossel mostra 2 cards ao invés de 3 em telas menores")
- Componentes globais que NÃO precisam de alteração (ex: sidebar, header)
-->

- [Estratégia de responsividade]

### 4.4 Navegacao por Teclado

<!-- Descreva atalhos de teclado e acessibilidade:
- Atalhos de abas (ex: tecla H para Histórico)
- Navegação em listas/carrosséis (Tab, Enter, setas)
- Condições (ex: "atalhos funcionam apenas quando nenhum input está em foco")
- Exibição visual dos atalhos (ex: elemento <kbd>)
- Instruções exibidas ao operador sobre atalhos disponíveis

Exemplo:
| Tecla | Ação                      | Exibição visual           |
| ----- | ------------------------- | ------------------------- |
| H     | Ir para aba Histórico     | <kbd>H</kbd> Histórico    |
-->

| Tecla | Acao | Contexto |
| ----- | ---- | -------- |
|       |      |          |

---

## 5. Nivel de Acesso (Permissoes)

<!-- Descreva o sistema de permissões usando 3 níveis:
- Nível 1: Acesso à feature (role básica, pré-requisito para todas as outras)
- Nível 2: Visualização de abas/seções (sem role = aba oculta)
- Nível 3: Ações específicas (sem role = botão oculto)

Inclua também:
- Grupos do Keycloak (agrupamento de roles para provisionamento)
- Perfis sugeridos (operador read-only, operador padrão, supervisor, admin)
- Implementação no frontend (rotas com guard, abas condicionais, botões condicionais)
-->

### 5.1 Catalogo de Roles

#### Nivel 1 -- Acesso a feature

| Role | Descricao |
| ---- | --------- |
|      |           |

<!-- Exemplo: `order-management-view` — Acesso básico: busca + visualização de detalhes -->

#### Nivel 2 -- Visualizacao de abas/secoes

| Role | Aba/Secao que desbloqueia |
| ---- | ------------------------- |
|      |                           |

<!-- Sem a role *-view correspondente, a aba inteira é ocultada. -->

#### Nivel 3 -- Acoes

| Role | Acao |
| ---- | ---- |
|      |      |

### 5.2 Grupos (Keycloak)

<!-- Agrupe as roles em grupos para facilitar o provisionamento.
Tipos de grupo:
- Acesso total à aba (todas as roles da aba)
- Acesso limitado (apenas algumas roles)
- Somente leitura (apenas roles de visualização)
- Admin (todas as roles da feature)
-->

#### Grupos por aba (acesso total)

| Grupo | Inclui automaticamente |
| ----- | ---------------------- |
|       |                        |

#### Grupos por aba (acesso limitado)

| Grupo | Inclui automaticamente |
| ----- | ---------------------- |
|       |                        |

#### Grupos somente leitura

| Grupo | Inclui automaticamente |
| ----- | ---------------------- |
|       |                        |

#### Grupo admin

| Grupo | Inclui automaticamente |
| ----- | ---------------------- |
|       |                        |

### 5.3 Perfis Sugeridos

<!-- Defina perfis típicos de operadores com os grupos que cada um recebe.
Exemplo:
| Perfil                        | Grupos atribuídos | Total |
| ----------------------------- | ----------------- | ----- |
| Operador somente-leitura      | read-only         | 1     |
| Operador padrão               | view + history + payments + items-read-only | 4 |
| Supervisor                    | view + todas *-full | 6   |
| Administrador                 | admin             | 1     |
-->

| Perfil | Grupos atribuidos | Total |
| ------ | ----------------- | ----- |
|        |                   |       |

### 5.4 Implementacao no Frontend

<!-- Descreva como as permissões são verificadas no código:
- Rotas: authorizationGuard com data.roles
- Abas: ocultar com @if baseado em hasAuthorization()
- Botões: ocultar com @if baseado em hasAuthorization()
- Service utilizado: o serviço de autorização do projeto (ex: authService.hasAuthorization())

Inclua exemplos de código quando útil.
-->

- **Rotas:** `authorizationGuard` com `data: { roles: [...] }`
- **Abas:** ocultar com `@if (authService.hasAuthorization([...]))`
- **Botoes:** ocultar com `@if (authService.hasAuthorization([...]))`

---

## 6. Tratamento de Erros

<!-- Descreva o padrão de tratamento de erros para TODAS as requisições da feature.
Use as tabelas abaixo como base e adapte conforme necessário.
-->

### 6.1 Respostas de Sucesso

| Status | Tipo | Comportamento no frontend |
| ------ | ---- | ------------------------- |
| `200`  | Sincrono | Acao confirmada. Exibe dados retornados ou snackbar de confirmacao |
| `201`  | Sincrono | Recurso criado. Exibe snackbar de confirmacao |
| `202`  | Assincrono | Acao aceita. Exibe snackbar/dialog com mensagem adequada ao contexto |

<!-- Especifique quais ações da feature usam cada status:
| Ação                              | Status esperado | Motivo                           |
| --------------------------------- | --------------- | -------------------------------- |
| Atualização de cadastro           | 200             | Síncrono — imediato              |
| Exportação de relatório           | 202             | Assíncrono, gerado em segundo plano |
-->

### 6.2 Respostas de Erro

| Status | Comportamento |
| ------ | ------------- |
| `400` | Erro de validacao — exibe mensagem retornada pela API |
| `401` | Nao autenticado — redirecionamento para login (interceptor existente) |
| `403` | Nao autorizado — tratado pelo interceptor existente |
| `404` | Recurso nao encontrado — mensagem informativa |
| `405`--`499` | Outros erros 4xx — exibe mensagem da API |
| `500+` | Erro interno — mensagem generica com orientacao para tentar novamente |

### 6.3 Regras Gerais

- Nunca silenciar erros: todo erro deve resultar em feedback visual ao operador
- Mensagem da API tem prioridade sobre mensagem generica
- Acoes destrutivas exigem **dialog de confirmacao** antes da requisicao
- Utilizar os utilitarios de tratamento de erro e de mensagens existentes no `shared/`

---

## 7. Dados de Exemplo (Mock)

<!-- Para CADA endpoint da feature, inclua:
- Método HTTP e rota
- JSON de exemplo da resposta
- Notas sobre o que é mockado vs. o que vem do backend
- Momento do carregamento (ao abrir tela, ao clicar em aba, sob demanda)

IMPORTANTE: Estes JSONs são dados de exemplo para guiar o desenvolvimento.
Não representam o contrato final com a API.
-->

### 7.1 [Nome do Endpoint / Contexto]

#### [METODO] `/rota/do/endpoint`

```json
{
  "exemplo": "dados"
}
```

<!-- Repita para cada endpoint. Agrupe por tela ou contexto (ex: "Mock da Busca", "Mock dos Detalhes", "Mock da Aba X"). -->

### 7.2 Comportamento de Carregamento

<!-- Descreva QUANDO cada dado é carregado:
| Contexto | Momento do carregamento | Estado inicial |
| -------- | ----------------------- | -------------- |
| Header   | Ao abrir a tela         | Loading > dados |
| Aba X    | Ao clicar na aba        | Loading > dados |
| Valor sensível | Ao clicar em visualizar | Oculto > Loading > valor |
-->

| Contexto | Momento do carregamento | Estado inicial |
| -------- | ----------------------- | -------------- |
|          |                         |                |

### 7.3 Paginacao

<!-- Diferencie claramente os dois tipos de paginação usados:
| Componente | Paginacao | page_size | Navegacao |
| ---------- | --------- | --------- | --------- |
| Carrossel  | Local no frontend | 100 | Setas navegam entre grupos de cards |
| Tabela     | Server-side | 10  | MatPaginator dispara nova requisição |
-->

| Componente | Paginacao | page_size | Navegacao |
| ---------- | --------- | --------- | --------- |
|            |           |           |           |

---

## 8. Componentes Angular Sugeridos

<!-- Liste os componentes do Angular Material (ou outros) que devem ser usados.
Inclua componentes custom necessários (ex: carrossel, card de resumo).
-->

| Componente | Uso | Referencia Angular Material |
| ---------- | --- | --------------------------- |
| `MatFormField` + `MatInput` | Campos de formulario | `@angular/material/input` |
| `MatTabGroup` / `MatTab` | Abas | `@angular/material/tabs` |
| `MatCard` | Cards | `@angular/material/card` |
| `MatChip` / Badge | Status (badges) | `@angular/material/chips` |
| `MatTable` + `MatPaginator` | Tabelas com paginacao | `@angular/material/table` |
| `MatSelect` | Dropdowns | `@angular/material/select` |
| `MatTooltip` | Tooltips | `@angular/material/tooltip` |
| `MatIcon` | Icones | `@angular/material/icon` |
| `MatDialog` | Modais | `@angular/material/dialog` |
| `MatButton` | Botoes | `@angular/material/button` |
|  |  |  |

<!-- Adicione componentes customizados necessários:
| Componente custom | Uso | Notas |
-->

---

## 9. Testes

### 9.1 Testes Unitarios (Vitest)

<!-- Descreva a expectativa de cobertura de testes unitários:
- Quais componentes, services, guards, pipes devem ser cobertos
- Framework utilizado (Vitest com @angular/build:unit-test)
- Regras especiais (ex: NÃO usar fakeAsync, TestBed.initTestEnvironment, etc.)
-->

Todos os componentes, services, guards, pipes e logica introduzidos por esta feature devem ter cobertura de testes unitarios utilizando Vitest.

### 9.2 Testes E2E (Playwright)

<!-- Descreva os fluxos E2E que devem ser cobertos:
- Fluxos principais (busca, navegação, ações críticas)
- Convenções (Page Object Model, data-testid, etc.)
- Se é uma introdução de E2E no projeto ou adição a suite existente
-->

Fluxos E2E a cobrir:
- [Fluxo 1]
- [Fluxo 2]

---

## 10. Referencia Visual

<!-- Inclua referências visuais (screenshots, mockups, wireframes).
Coloque os arquivos de imagem na mesma pasta docs/ do módulo.
IMPORTANTE: Em caso de discrepância entre imagens e texto do spec, o TEXTO tem precedência.
-->

Os layouts de referencia estao na mesma pasta `docs/` deste modulo:

1. **[Nome da tela]** -- [`imagem-1.png`](imagem-1.png)
   ![Descricao](imagem-1.png)

> Os layouts sao referencia visual. As decisoes documentadas neste spec tem prioridade sobre detalhes visuais do prototipo.

---

## 11. Prompt para Desenvolvimento

<!-- OBRIGATÓRIO: Preencha as seções marcadas com [PREENCHER] abaixo.
As partes genéricas do prompt já estão incluídas — apenas complete as partes específicas da feature.
O resumo das telas e requisitos transversais deve ser um resumo conciso do spec, NÃO uma cópia integral.
-->

```
Preciso implementar a feature "[PREENCHER: Nome da Feature]" no projeto Angular.

Documentos de referência:
- `[PREENCHER: caminho do módulo]/docs/spec-tela-[PREENCHER].md` — especificação completa da feature (este documento)
- `templates/project-reference.template.md` — referência técnica do projeto (arquitetura, padrões, stack, guia de implementação)

Leia ambos os documentos antes de prosseguir.

ESCOPO: [PREENCHER: escopo da implementação, o mesmo da seção 1 (frontend-only / full-stack / outro). Ex.: apenas frontend, com dados de mocks locais e os endpoints do spec só como referência.]

AMBIENTE DE DESENVOLVIMENTO: Durante a implementação o projeto estará rodando via `<DEV_CMD>` e disponível para acesso em <DEV_URL>. Os agentes podem utilizar este endereço para verificação visual das telas implementadas se necessário.

MODELO DOS SUBAGENTES: Orquestração, design técnico e code review DEVEM usar o modelo mais capaz disponível na ferramenta de AI em uso (no Claude Code, model: "opus"). Os demais subagentes seguem a estratégia de modelo escolhida no início da sessão (Passo 1.5 de `processes/start-workflow.md`).

WORKFLOW: Seguir o processo documentado em `docs/workflow.md`. Em resumo:

1. **Etapa de discovery (obrigatória, no agente principal):** Antes de qualquer produção de documentos, faça uma varredura do codebase para entender a arquitetura, padrões e convenções existentes. Ao final, produza um documento detalhado de discovery (`docs/discovery.md`) contendo:
   - Lista de arquivos essenciais do projeto com caminhos completos (rotas, sidebar-data, guards, services, componentes de referência, etc.)
   - Trechos relevantes extraídos desses arquivos (ex: estrutura de rotas, padrão de um módulo existente, configuração de interceptors)
   - Padrões e convenções identificados que devem ser seguidos
   - Este documento será passado como referência para todos os subagentes subsequentes, evitando que cada um precise refazer a varredura.

2. **Delegação para subagentes:** Após o discovery, delegue a produção de documentos extensos (design, tasks, relatório final) para **subagentes dedicados**. O agente principal atua como **orquestrador**: define o escopo, delega a escrita passando no prompt os caminhos dos arquivos de referência (spec, discovery, referência do projeto) para o subagente ler, revisa o resultado e prossegue para a próxima etapa.

3. **Implementação paralela:** Na fase de implementação, utilizar subagentes em paralelo com worktree isolation para tarefas independentes, sempre passando o discovery como contexto.

4. **Code review obrigatório:** Após cada fase de implementação, despachar subagente de code review que: lê todos os arquivos, compara com spec/design, executa lint + typecheck + SonarQube + testes, corrige automaticamente issues que não precisem de decisão do usuário.

5. **Testes E2E:** Seguir o padrão POM (Page Object Model) com `data-testid` conforme documentado em `docs/e2e.md`.

[PREENCHER: Resumo conciso das telas da feature. Para cada tela, listar:
- Rota
- Elementos principais (formulários, tabelas, cards, abas)
- Ações disponíveis
- Regras de negócio críticas

Exemplo:
## Tela 1: Busca de Pedidos (/orders)
- Nova seção "PEDIDOS" no menu lateral com item "Buscar"
- Formulário com 3 campos: Número do pedido, CPF/CNPJ do cliente, Email
- Resultados em carrossel horizontal de cards
...]

## Requisitos transversais:
[PREENCHER: Listar requisitos que se aplicam a todas as telas:
- Logging/auditoria
- Tratamento de erros
- Navegação por teclado
- Responsividade
- Dark mode
- Componentes reutilizáveis]

## Testes:
- Testes unitários (Vitest) cobrindo todos os componentes, services e lógica introduzidos
- Testes E2E (Playwright) com Page Object Model e data-testid, cobrindo fluxos principais

## Referências visuais:
[PREENCHER: Descrever imagens de referência anexadas, se houver]

IMPORTANTE: Estas imagens são referências de BAIXA FIDELIDADE. Devem ser tratadas apenas como guia visual para layout e hierarquia de informações. Em caso de qualquer discrepância entre as imagens e o texto do documento de especificação, o TEXTO do documento tem precedência absoluta.

## Documentação do processo (OBRIGATÓRIO):
Todo o processo de implementação desta feature será documentado. Durante CADA estágio do processo (brainstorm, spec, design, tasks, implementação), você DEVE:
1. Documentar minuciosamente todas as decisões tomadas e suas justificativas
2. Registrar toda e qualquer descoberta sobre o codebase, padrões, limitações ou oportunidades
3. Anotar informações que possam ser úteis e/ou relevantes para futuras implementações similares
4. Registrar dificuldades encontradas, como foram resolvidas e o que poderia ter sido feito diferente
5. Documentar desvios do plano original e os motivos

Todos os documentos gerados durante o processo devem ser salvos na pasta `[PREENCHER: caminho do módulo]/docs/`, organizado em subpastas por estágio quando necessário (ex: `docs/brainstorm/`, `docs/design/`, `docs/tasks/`, etc.).

Ao final da implementação, gerar um **documento de relatório final** na pasta `docs/` contendo:
- Resumo do que foi implementado vs. o que foi especificado
- Decisões técnicas tomadas durante a implementação e suas justificativas
- Descobertas relevantes sobre o codebase
- Dificuldades encontradas e soluções adotadas
- Lições aprendidas para futuras implementações com AI
- Métricas: número de componentes criados, cobertura de testes, etc.

## Framework de follow-up pós-entrega:
Ao final, gerar também uma seção de follow-up no relatório contendo:
1. **Lista de itens pendentes** — edge cases não cobertos, funcionalidades parcialmente implementadas, TODOs no código
2. **Bugs conhecidos** — problemas identificados mas não corrigidos na entrega inicial, com severidade e contexto
3. **Melhorias sugeridas** — otimizações, refatorações ou melhorias de UX identificadas durante a implementação
4. **Dívida técnica** — atalhos tomados conscientemente que precisam ser endereçados
5. **Checklist de validação** — lista de verificações manuais a serem feitas antes de considerar a feature "pronta para produção"

Comece pelo brainstorm e depois siga o fluxo completo de spec > design > tasks > implementação.
```
