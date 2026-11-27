---
name: create-work-item
description: "Use quando precisar criar ou vincular um item de trabalho no board configurado no projeto."
---

# Create Work Item — Vincular ou Criar Item de Trabalho

Consulte o fluxo do board registrado em `.claude/PROJECT_REFERENCE.md` ou na documentação do time. Siga as [convenções de itens de trabalho](../docs/processo-work-items.md) e use o conector configurado para o tracker. Se não houver board, ofereça acompanhamento local. Se a configuração estiver indefinida, confirme antes de criar ou mover itens.

---

## 1. Hierarquia de referência

Mapeie estes papéis para os tipos e vínculos disponíveis no fluxo do time.

```
Feature              ← Ticket de alto nível, define o escopo geral
 └─ User Story       ← Caso de uso da Feature, entrega valor ao negócio
     └─ Task         ← Esforço granular para entregar a User Story
```

Regras:

- **Feature:** contextualização macro do problema (quem é afetado, como pretendemos solucionar). Não entra em detalhes técnicos. Não serve como diário da implementação;
- **User Story:** entrega que gera valor ao negócio. Vincule à Feature equivalente quando o fluxo do time usar esse nível;
- **Task:** atividade concreta para que a User Story chegue em produção. Descrição opcional quando o título for suficiente;
- **Bug:** use o tipo ou a classificação de defeito adotada no board.

---

## 2. Padrões de Título

### Feature
Título descritivo do escopo. Exemplo: `Gerenciamento de Pedidos`.

### User Story
User Stories representam **ações que entregam valor**. O título é a forma
**nominal/substantivada** da ação. Mnemônico: pergunte "que ação eu vou fazer?"
e substantivize a resposta — sem verbo no infinitivo, sem o meio (tela/serviço).

| Pergunta                 | Resposta (verbo)           | Título da US (substantivo)        |
| ------------------------ | -------------------------- | --------------------------------- |
| "que ação eu vou fazer?" | "Vou visualizar histórico" | `Visualização de Histórico`       |
| "que ação eu vou fazer?" | "Vou enviar o relatório"   | `Envio de Relatório Mensal`       |
| "que ação eu vou fazer?" | "Vou cancelar o pedido"    | `Cancelamento de Pedido`          |
| "que ação eu vou fazer?" | "Vou buscar pedido"        | `Busca de Pedido`                 |
| "que ação eu vou fazer?" | "Vou notificar por SMS"    | `Notificação por SMS`             |

| Correto                  | Errado                            | Razão                                       |
| ------------------------ | --------------------------------- | ------------------------------------------- |
| `Busca de Pedido`        | `Buscar Pedido`                   | Não usar verbo no infinitivo no título      |
| `Busca de Pedido`        | `Tela de Busca de Pedido`         | Foco no objetivo (ação), não no meio (tela) |
| `Notificação por SMS`    | `Implementar Notificação por SMS` | Implementação é Task; US é o valor entregue |
| `Cancelamento de Pedido` | `Cancelar Pedido`                 | Sempre forma nominal/substantivada          |

Limite: **≤70 caracteres**. Se ultrapassar, decompor em mais de uma estória.

### Task
**Verbos no infinitivo**, descritivo da ação. Exemplos:

- `Criar serviço xpto`;
- `Criar endpoint xyz`;
- `Prototipar/Implementar Tela xyz`;
- `Criar modelo DER`;
- `Realizar testes unitários`;
- `Criar/Abrir Pull Request`;
- `Gerar Evidências`;
- `Preparar GMUD`;
- `Publicar Estória`.

### Bug
Título descritivo do problema observado. Exemplo: `[APP][API] Falha ao gerar relatório de pedidos`.

---

## 3. Template da User Story (descrição e critérios de aceite)

Organize a demanda e os critérios de aceite em blocos distintos, usando os campos ou o template do board.

### 3.1 Descrição

```
DEMANDA

Eu, como [Stakeholder],
Necessito que [Descrição da necessidade],
Para que eu [Um breve contexto].

CONTEXTO

[Contexto detalhado e reflexo de indicadores, quando houver].

PROTÓTIPOS/LINKS IMPORTANTES:

[Quando houver].
```

### 3.2 Critérios de aceite

Use o campo dedicado se estiver disponível para o tipo de item. Na ausência dele, use a seção **Critérios de aceite** da descrição ou o local previsto no template do board. Liste critérios verificáveis, de preferência em Gherkin quando aplicável:

```
- Dado [pré-condição], quando [ação], então [resultado esperado];
- O botão "Salvar" só fica habilitado quando todos os campos obrigatórios estão preenchidos;
- Mensagem de erro X aparece quando o CPF é inválido.
```

Regras de redação:

- **DEMANDA:** o mais resumido e sucinto possível;
- **CONTEXTO:** máximo de detalhes para o time entender o que precisa ser feito;
- **PROTÓTIPOS/LINKS:** opcional, incluir apenas quando houver;
- **Acceptance Criteria:** explícitos e verificáveis (cada item testável objetivamente).

---

## 4. Regras de formatação de listas

Sempre que devolver instruções em lista:

- A introdução da lista deve começar com `:`;
- Itens da lista devem terminar com `;`, exceto o último;
- O último item da lista deve terminar com `.`.

Esta própria seção é exemplo do padrão.

---

## 5. Padrão de prototipação

Quando o desenvolvimento envolve protótipo, usar o seguinte padrão:

- **Implementação inicial:** registrada dentro de uma User Story de **prototipação**, mesmo se cobrir grande parte do escopo;
- **Polimento / produção:** após o follow-up, o que deixa de ser protótipo é registrado em uma **nova User Story** que representa a entrega para produção;
- A User Story de prototipação fica `Resolved` quando o protótipo está pronto; a US de produção é criada na sequência para cobrir o polimento final.

Exemplo aplicado: `Prototipação de telas de Cadastro de pedidos` (US #1234) cobriu toda a implementação inicial; o polimento da tela de cadastro virou a US `Cadastro de Pedidos` separada.

---

## 6. Tasks padrão

### Última Task (User Story e Bug)
Sempre incluir como **última** Task:

- US: `Gerar evidência da estória`;
- Bug: `Gerar evidências de correção`.

### Primeira Task (Bug somente)
Para Bugs, incluir como **primeira** Task: `Analisar problema`.

> **Importante:** "Analisar problema" não se aplica a User Stories — US começam direto pela primeira ação concreta de implementação.

### Tasks intermediárias
Listar ações concretas no infinitivo. Quantidade proporcional à complexidade (típico: 6–14 tasks). Idealmente antecipar todas no momento de criar a US, mas é aceitável adicionar novas conforme o progresso revela necessidades não previstas.

---

## 7. Comportamento conversacional

Ao montar work items com o usuário:

- **Numerar** as perguntas para facilitar a resposta (ex: `1. ...`, `2. ...`, `3. ...`);
- **Sempre confirmar** antes de assumir um valor (ex: stakeholder, área, iteração);
- **Pedir contexto** quando algum serviço, banco de dados, tabela ou similar for citado, para entender se deve ou não ser alterado;
- **Questionar** quando faltarem detalhes nas informações fornecidas;
- Sugerir valores razoáveis (ex: stakeholder provável) **mas confirmar** antes de aplicar.

---

## 8. Fluxo da skill

Perguntar ao usuário:

> Quer vincular este trabalho a um item no board do projeto?
>
> 1. Já tenho o ID do work item — informar o ID;
> 2. Criar um novo work item agora seguindo o processo (Feature/User Story/Task/Bug);
> 3. Pular — trabalhar sem work item (apenas diário local).

### Opção 1 — Work item existente

Pedir o ID ou URL e validar pelo conector configurado. Exemplo para Azure DevOps:

```
mcp__azure-devops__wit_get_work_item({ project: "<AZURE_PROJECT>", id: [ID] })
```

Confirmar título, tipo, parent e estado com o usuário antes de prosseguir.

### Opção 2 — Criar novo

Perguntar **uma pergunta por vez**, numerando:

1. Tipo do work item (`Feature`, `User Story`, `Task`, `Bug`);
2. Título (validar contra os padrões da seção 2 acima);
3. Item pai ou vínculo equivalente, quando o fluxo exigir. Validar pelo conector que o item existe e é compatível;
4. Para User Story: redigir descrição e critérios de aceite conforme a seção 3. Para Bug, registrar o comportamento esperado e como verificar a correção;
5. Para Task: descrição opcional (perguntar se necessária);
6. Campos obrigatórios no board, como área, time ou iteração, quando aplicáveis.

#### Validações antes de criar

- Item sem vínculo exigido pelo board: pedir o item pai ou a referência equivalente;
- Correção de bug: usar a classificação adotada pelo board;
- Título de US começando com verbo no infinitivo ou contendo "Tela de": sugerir reformulação;
- Título com mais de 70 caracteres: sugerir decompor.

#### Criar pelo conector configurado

Use os campos e operações do board. Os exemplos abaixo são de Azure DevOps. Inclua `Microsoft.VSTS.Common.AcceptanceCriteria` apenas quando o campo existir no tipo configurado.

```
mcp__azure-devops__wit_create_work_item({
  project: "<AZURE_PROJECT>",
  workItemType: "[tipo]",
  fields: [
    { name: "System.Title", value: "[título]" },
    { name: "System.Description", value: "[DEMANDA + CONTEXTO + PROTÓTIPOS]", format: "Markdown" },
    // Para User Story / Bug — Critérios de Aceite no campo dedicado:
    { name: "Microsoft.VSTS.Common.AcceptanceCriteria", value: "[lista de critérios verificáveis]", format: "Markdown" },
    { name: "System.AreaPath", value: "<AREA_PATH>" },
    // ...demais campos
  ]
})
```

> Para Tasks, normalmente o campo Acceptance Criteria não é usado — Tasks são
> ações concretas (não entregas de valor verificáveis). Inclua AC apenas em
> User Stories e Bugs.

Quando fizer parte do fluxo do time, crie também as tarefas antecipadas como filhas ou vinculadas. Exemplo para Azure DevOps:

```
mcp__azure-devops__wit_add_child_work_items({
  parentId: [US criada],
  workItemType: "Task",
  items: [
    { title: "Primeira Task no infinitivo", description: "[opcional]" },
    // ...demais tasks
    { title: "Gerar evidência da estória", description: "" }
  ]
})
```

Para conectar US a Feature pai (se a US foi criada solta):

```
mcp__azure-devops__wit_add_child_work_items({
  parentId: [Feature ID],
  childIds: [US criada]
})
```

### Opção 3 — Pular

Registrar que não há item vinculado. Para registro de horas, aplique as regras do provedor configurado e registre no diário quando um vínculo obrigatório estiver ausente.

---

## 9. Casos especiais

### Componente compartilhado descoberto durante uma feature
Componentes shared (ex: tabela paginada, header genérico) devem ter como **parent uma Feature de melhorias** (ex: uma Feature `Melhorias`), não a Feature da feature em curso, já que entregam valor ao projeto de modo geral. Confirmar com o usuário antes de mover.

### Discussão vs. Tasks
Quando houver um esforço/ação, criar uma **Task** ao invés de usar a seção `Discussion` do ticket. Comentários da Discussion são para detalhes adicionais relevantes que não comportam um Task próprio.

### Estado do item ao abrir PR ou MR

Vincule o PR/MR ao item após confirmar a abertura e siga as [transições do board](../docs/processo-work-items.md#35-ciclo-de-vida-e-transições-de-estadocoluna). Consulte o mapeamento do projeto para saber o estado de destino, quando um rascunho entra em revisão e se a transição cabe ao agente, a uma automação ou a uma pessoa.

---

## 10. Retorno

Esta skill retorna ao fluxo chamador com:

- `workItemId`: ID do work item (ou null se pulou);
- `workItemType`: `Feature`, `User Story`, `Task` ou `Bug`;
- `workItemTitle`: título para referência nos documentos;
- `parentId`: ID do parent (quando aplicável).
