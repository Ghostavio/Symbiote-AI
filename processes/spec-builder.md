---
name: spec-builder
description: "Use quando o usuário quiser criar uma nova especificação de feature para o projeto a partir do template padrão."
---

# Spec Builder — Construtor de Especificações

Guia o usuário na criação de um documento de especificação completo para novas features do projeto, seguindo o template padrão e coletando informações seção por seção através de diálogo colaborativo.

## Documentos de Referencia

- **Template:** `templates/spec-template.md` — estrutura base que será preenchida
- **Spec de exemplo:** um spec completo já existente no projeto (quando houver) — serve de referência de nível de detalhe
- **Workflow:** `docs/workflow.md` — processo de desenvolvimento que o spec alimenta
- **Referência técnica:** `.claude/PROJECT_REFERENCE.md` ou a referência indicada pelo projeto. Use `templates/project-reference.template.md` como modelo quando a referência ainda não existir.

## Hard Gate

<HARD-GATE>
NÃO gere o spec final até ter passado por TODAS as etapas do checklist abaixo.
NÃO pule etapas mesmo que o usuário diga que a feature é "simples".
NÃO faça mais de uma pergunta por mensagem.
NÃO comece a implementar nada — esta skill produz APENAS o documento de especificação.
</HARD-GATE>

## Checklist

Use os passos abaixo como checklist local e complete-os em ordem:

1. **Preparar contexto** — ler o template, a referência técnica e o spec de exemplo (quando houver)
2. **Entender o escopo** — qual feature, quantas telas, público-alvo, escopo (frontend-only?) e vínculo com um item do board, quando aplicável
3. **Definir navegação** — onde no menu lateral, fluxo entre telas, rotas, breadcrumbs
4. **Detalhar cada tela** — layout, formulários, campos, botões, regras, estados, modais
5. **Definir componentes reutilizáveis** — componentes compartilhados entre telas
6. **Definir regras transversais** — logging, cores, responsividade, acessibilidade, teclado
7. **Definir permissões** — roles em 3 níveis, grupos do provedor de identidade (IdP), perfis sugeridos
8. **Definir dados mock** — JSONs para cada endpoint, comportamento de carregamento
9. **Definir tratamento de erros** — status codes e comportamento no frontend
10. **Definir testes** — unitários e E2E esperados
11. **Revisar spec completo** — apresentar resumo e validar com o usuário
12. **Salvar** — gerar o arquivo .md na pasta docs do módulo

## Fluxo do Processo

```
Preparar contexto
       |
       v
Entender o escopo (perguntas gerais)
       |
       v
Definir navegacao (sidebar, rotas, fluxo)
       |
       v
Detalhar Tela 1 --> Detalhar Tela 2 --> ... Tela N
(para cada tela: layout, campos, botoes, regras, estados, modais)
       |
       v
Componentes reutilizáveis
       |
       v
Regras transversais (logging, cores, responsividade, teclado)
       |
       v
Permissões (roles, grupos, perfis)
       |
       v
Dados mock (JSONs, carregamento, paginação)
       |
       v
Tratamento de erros
       |
       v
Testes (unitários, E2E)
       |
       v
Revisão final com usuário
       |
       v
Salvar spec em docs/
```

## O Processo

### Etapa 1 — Preparar Contexto

Antes de fazer qualquer pergunta, leia silenciosamente:
1. O template em `templates/spec-template.md`
2. A referência técnica do projeto, incluindo a seção **Board e Fluxo de Trabalho**, quando houver
3. Se o projeto já tiver um spec completo, as primeiras 100 linhas dele, para relembrar o nível de detalhe esperado

NÃO exiba o conteúdo destes arquivos ao usuário. Apenas use como contexto interno.

### Etapa 2 — Entender o Escopo

Faça UMA pergunta por vez. Comece com:

> Vamos construir a especificação da sua nova feature. Para começar, me conte:
> **Qual é a feature que você quer especificar?** Descreva em 1-2 frases o que ela faz.

Depois, continue com perguntas individuais:

- **Quantas telas** compõem a feature? Liste o nome de cada uma.
- **Qual o público-alvo?** (ex: operadores de atendimento, supervisores, administradores)
- **O escopo é apenas frontend?** Ou inclui backend/API?
  - (a) Apenas frontend — endpoints servem como referência para mocks
  - (b) Full-stack — inclui implementação de backend
  - (c) Outro — descreva
- **Existe algum módulo existente** no projeto que serve de referência ou que será integrado?
- **Existem documentos de referência** (reuniões, protótipos, layouts)? Se sim, compartilhe os links.
- **Vínculo com o board, quando aplicável:** consulte a referência do projeto. Se o board estiver indefinido, confirme qual usar antes de propor um vínculo. Quando o projeto trabalhar sem board, siga com a documentação local sem pedir um ID.
  - **Vincular item existente:** aceite ID, chave ou URL e confirme o item no tracker configurado. Se o conector estiver indisponível, peça a referência manual e indique que ela ainda precisa de verificação.
  - **Criar item:** somente a pedido do usuário, use [create-work-item](create-work-item.md) com os tipos, campos e vínculos do board. Solicite um item pai apenas quando o fluxo exigir.
  - **Adiar ou seguir sem vínculo:** registre a escolha e continue a especificação.
  - Registre o tracker, a referência do item e a URL, quando conhecida, nos metadados do spec. Use o item como pai somente quando o board e o fluxo do time definirem esse vínculo. O registro de horas é configurado separadamente.

### Etapa 3 — Definir Navegação

- **Onde a feature aparece no menu lateral?**
  - (a) Nova seção no menu — qual o nome?
  - (b) Dentro de uma seção existente — qual?
  - (c) Não aparece no menu (acessada de outro lugar)
- Para cada item de menu: **nome, ícone e rota**
- **Alguma tela não possui item no menu?** (ex: tela de detalhes acessada via botão)
- **Qual o fluxo entre as telas?** Vou montar um diagrama ASCII para você validar.
- **Quais telas possuem breadcrumb?** Qual o texto de cada nível?

### Etapa 4 — Detalhar Cada Tela

Para CADA tela, passe por estas subperguntas (uma por vez):

**Layout:**
- Qual o título e subtítulo da tela?
- Quais são as áreas/seções principais? (ex: formulário no topo, resultados embaixo)
- A tela possui abas? Quantas e quais?

**Formulários:**
- Quais campos de formulário existem? Para cada campo, vou perguntar:
  - Nome e placeholder
  - Tipo (texto, email, select, date, textarea, checkbox, etc.)
  - Máscara (CPF, CNPJ, celular, CEP, etc.)
  - Validações (obrigatório, formato, tamanho)
- Oferecer opções de máscara quando aplicável:
  - (a) CPF: `000.000.000-00`
  - (b) CNPJ: `00.000.000/0000-00`
  - (c) CPF/CNPJ dinâmico (baseado no número de caracteres)
  - (d) Celular: `(00) 00000-0000`
  - (e) CEP: `00000-000`
  - (f) Moeda: `R$ 0.000,00`
  - (g) Outra — descreva

**Botões:**
- Quais botões existem na tela? Para cada um: nome, ícone, ação, cor.
- Algum botão é condicional (visível apenas com permissão ou estado)?

**Exibição de dados:**
- Como os dados são exibidos?
  - (a) Tabela com paginação server-side
  - (b) Carrossel de cards com paginação local
  - (c) Lista simples
  - (d) Cards estáticos
  - (e) Outro — descreva
- Quais campos/colunas são exibidos em cada item?
- Existe ordenação? Qual o padrão?

**Estados:**
- Além dos estados padrão (inicial, carregando, com dados, vazio, erro), existe algum estado especial?

**Modais:**
- A tela abre algum modal/dialog? Para cada modal:
  - Quando é aberto (qual ação/botão)
  - Quais campos possui
  - Qual o fluxo (passos)
  - Existe aviso/warning no modal?

### Etapa 5 — Componentes Reutilizáveis

- **Existe algum componente usado em múltiplos contextos?** (ex: carrossel, card de status)
- Para cada componente reutilizável:
  - Onde é usado (listar contextos)
  - Comportamento (quantidade de itens visíveis, navegação, contador)
  - Responsividade (adaptações para telas menores)

### Etapa 6 — Regras Transversais

- **Logging:** Quais ações geram log? O log é automático pelo backend ou precisa de implementação no frontend?
- **Cores:**
  - Quais status/estados usam cores diferenciadas? (montar tabela de mapeamento)
  - Existe regra de fallback para status não mapeados?
  - Considerar dark mode?
- **Responsividade:**
  - (a) Desktop-first (ferramenta interna)
  - (b) Mobile-first
  - (c) Ambos
  - Qual o breakpoint mínimo? (ex: 960px para tela dividida)
- **Navegação por teclado:**
  - A feature terá atalhos de teclado?
  - Quais teclas para quais ações?
  - Exibir indicadores visuais (elemento `<kbd>`)?

### Etapa 7 — Permissões

- **Qual a role básica de acesso à feature?** (nível 1)
- **Quais abas/seções precisam de role própria?** (nível 2) — listar
- **Quais ações precisam de role própria?** (nível 3) — listar
- Vou propor a estrutura de roles seguindo o padrão `[módulo]-[contexto]-[ação]`. Validar.
- **Grupos do provedor de identidade (IdP):**
  - Acesso total por aba
  - Acesso limitado
  - Somente leitura
  - Admin
- **Perfis sugeridos:** Vou propor 3-4 perfis típicos com os grupos correspondentes. Validar.

### Etapa 8 — Dados Mock

Para cada endpoint/contexto:
- **Qual a rota e método HTTP?**
- **Qual o formato do JSON de resposta?** (vou propor um exemplo baseado nos campos já definidos)
- **Quando os dados são carregados?** (ao abrir tela, ao clicar em aba, sob demanda)
- **Qual o tipo de paginação?** (local no frontend com page_size=100, ou server-side com page_size=10)

### Etapa 9 — Tratamento de Erros

- **As ações da feature usam respostas síncronas (200) ou assíncronas (202)?**
  - Para cada ação, definir o status esperado e o motivo
- **Existe algum tratamento de erro específico** além do padrão? (ex: dialog especial para 404)
- Confirmar uso dos handlers de erro e de mensagens que o projeto já tem (se houver)

### Etapa 10 — Testes

- **Testes unitários:** Confirmar cobertura de todos os componentes, services, guards, pipes
- **Testes E2E:** Quais fluxos devem ser cobertos?
  - Listar os fluxos principais
  - Definir prioridade (crítico, importante, nice-to-have)

### Etapa 11 — Revisão Final

Apresentar um **resumo estruturado** do spec completo (não o documento final, mas uma visão geral) para o usuário validar:

> Aqui está o resumo do spec que vamos gerar:
>
> **Feature:** [nome]
> **Item no board:** [tracker, ID/chave ou URL, "vínculo adiado" ou "sem vínculo"]
> **Telas:** [lista]
> **Navegação:** [fluxo resumido]
> **Roles:** [quantidade total]
> **Endpoints:** [quantidade total]
> **Modais:** [lista]
> **Componentes reutilizáveis:** [lista]
>
> Posso gerar o documento completo? Ou quer ajustar algo?

Se o usuário pedir ajustes, voltar para a etapa relevante e refazer.

### Etapa 12 — Salvar

1. Gerar o spec completo preenchendo o template com TODAS as informações coletadas
2. Salvar em: `<src>/modules/[nome-do-modulo]/docs/spec-tela-[nome-da-feature].md` (ou caminho de módulos definido em `.claude/PROJECT_REFERENCE.md`)
   - Se o diretório `docs/` não existir no módulo, criar
   - Se o módulo ainda não existir, salvar em `docs/specs/spec-[nome-da-feature].md`
3. Commitar com mensagem: `docs: adicionar especificação da feature [nome]`

> Spec salvo em `[caminho]`. Revise o documento e me avise se quiser fazer ajustes.
> Quando estiver satisfeito, você pode usar o workflow de desenvolvimento (`/brainstorming` ou prompt direto) para iniciar a implementação.

Opcional: quem preferir um fluxo de spec com subagentes dedicados (requisitos, design e tarefas) pode instalar à parte a extensão Kiro for Claude Code (https://github.com/notdp/kiro-for-cc). Ela não vem no kit e tem licença própria (AGPL-3.0). O fluxo acima funciona sem ela.

## Princípios

- **Uma pergunta por vez** — não sobrecarregue o usuário com múltiplas perguntas
- **Oferecer opções** — use multiple choice sempre que possível (a, b, c, d)
- **Propor e validar** — proponha respostas quando tiver contexto suficiente, deixe o usuário corrigir
- **Nível de detalhe do spec de referência** — quando houver spec de exemplo no projeto, o documento gerado deve ter o mesmo nível de detalhe dele; sem spec de exemplo, preencha todas as seções de `templates/spec-template.md`
- **Sem suposições silenciosas** — se algo não ficou claro, pergunte. Não preencha com suposições
- **Português brasileiro** — todas as perguntas, instruções e o documento final em pt-BR
- **Tabelas formatadas** — usar tabelas markdown para campos, roles, mocks, etc.
- **Exemplos concretos** — incluir exemplos reais nos JSONs de mock e nas descrições

## Dicas para o Facilitador

- Se o usuário fornecer um documento de requisitos/protótipo, leia-o antes de começar as perguntas e adapte o fluxo (pule perguntas já respondidas, foque nas lacunas)
- Se a feature for muito grande (5+ telas), sugira decompor em sub-features com specs separados
- Se o usuário não souber responder algo (ex: "não sei quais permissões"), proponha uma estrutura padrão baseada no spec de referência (quando houver) ou em `templates/spec-template.md` e pergunte se faz sentido
- Ao detalhar campos de formulário, pergunte sobre máscaras (ex.: CPF, CNPJ, celular, CEP, moeda) quando o projeto lidar com esses dados
- Para cores de status, sempre inclua um fallback (laranja para status não mapeados)
- Para paginação, sempre clarifique: local no frontend (carrossel) vs. server-side (tabela)
