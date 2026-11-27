# Processo de Work Items

> Referência para criação e organização de itens de trabalho no board configurado no projeto. Humanos e agentes seguem as mesmas convenções (ver [create-work-item](../processes/create-work-item.md)).

---

## 1. Hierarquia

Use a estrutura abaixo como referência. Mapeie os níveis para os tipos e vínculos adotados no board do time. Quando a ferramenta não oferecer uma hierarquia equivalente, use os vínculos disponíveis ou referencie o item pai na descrição, conforme a convenção do projeto. Peça confirmação se o mapeamento estiver indefinido.

```
Feature              ← Ticket de alto nível, define o escopo geral
 └─ User Story       ← Casos de uso da Feature (entrega valor ao negócio)
     └─ Task         ← Esforço técnico granular para entregar a User Story
```

---

## 2. Ticket de Feature (Ponto de Partida)

Contextualização macro do problema, incluindo:

- Quem está sendo afetado;
- Como pretendemos solucioná-lo.

Não deve entrar em detalhes técnicos sobre a implementação. **Nunca** serve como diário do que aconteceu durante a implementação — é um ponto de partida explicando o problema e a proposta de solução.

---

## 3. Tickets de User Stories

Uma User Story descreve uma entrega que gera valor ao negócio. Vincule-a ao item que representa sua Feature quando essa hierarquia fizer parte do fluxo do time. Para correções, use o tipo ou a classificação de bug adotada no board.

### 3.1 Título

User Stories representam **ações que entregam valor**. O título é a forma
**nominal/substantivada** da ação (responda "que ação eu vou fazer?" e
substantivize a resposta — sem verbo no infinitivo, sem o meio/tela):

| Pergunta                 | Resposta (verbo)           | Título da US (substantivo)        |
| ------------------------ | -------------------------- | --------------------------------- |
| "que ação eu vou fazer?" | "Vou visualizar histórico" | `Visualização de Histórico`       |
| "que ação eu vou fazer?" | "Vou enviar o relatório..." | `Envio de Relatório Mensal`      |
| "que ação eu vou fazer?" | "Vou cancelar o pedido"    | `Cancelamento de Pedido`          |
| "que ação eu vou fazer?" | "Vou buscar pedido"        | `Busca de Pedido`                 |
| "que ação eu vou fazer?" | "Vou notificar por SMS"    | `Notificação por SMS`             |

| ✅ Correto               | ❌ Errado                         | Razão                                       |
| ------------------------ | --------------------------------- | ------------------------------------------- |
| `Busca de Pedido`        | `Buscar Pedido`                   | Não usar verbo no infinitivo no título      |
| `Busca de Pedido`        | `Tela de Busca de Pedido`         | Foco no objetivo (ação), não no meio (tela) |
| `Notificação por SMS`    | `Implementar Notificação por SMS` | Implementação é Task; US é o valor entregue |
| `Cancelamento de Pedido` | `Cancelar Pedido`                 | Sempre forma nominal/substantivada          |

O título deve resumir o que será feito na demanda e **de preferência não ultrapassar 70 caracteres**.

### 3.2 Formato da descrição

```
DEMANDA

Eu, como [Stakeholder],
Necessito que [Descrição da necessidade],
Para que eu [Um breve contexto].

CONTEXTO

[Contexto mais detalhado e reflexo de indicadores, quando houver].

PROTÓTIPOS/LINKS IMPORTANTES:

[Quando houver].
```

### 3.2.1 Critérios de aceite

Use o campo dedicado de critérios de aceite quando ele estiver disponível para o tipo de item no board configurado. Siga o nome e o formato definidos pelo projeto. Na ausência desse campo, registre os critérios em uma seção **Critérios de aceite** na descrição ou no local previsto pelo template do board. Registre a lista uma única vez.

Listar critérios verificáveis, um por linha, em formato de lista. Exemplo:

```
- Dado [pré-condição], quando [ação], então [resultado esperado];
- O botão "Salvar" só fica habilitado quando todos os campos obrigatórios estão preenchidos;
- Mensagem de erro X aparece quando o CPF é inválido.
```

Boas práticas:

- Cada critério deve ser **verificável** (testável objetivamente);
- Evitar critérios vagos ("a tela deve funcionar bem") — preferir métricas/comportamentos específicos;
- Quando aplicável, usar o formato Gherkin (`Dado / Quando / Então`).

### 3.3 Diretrizes de redação (descrição e critérios de aceite)

- A parte `Eu, como [Stakeholder], necessito que [...], para que [...]` precisa ser o mais resumida e sucinta possível;
- Na parte `CONTEXTO`, deve ter o máximo de detalhes possíveis para que o time entenda o que precisa ser feito;
- Use os comentários do item para detalhes adicionais relevantes e o diário para registrar a implementação;
- Registre ações de trabalho como tarefas ou itens vinculados, conforme a convenção do board.

### 3.4 Comportamento conversacional ao montar uma User Story

Ao auxiliar na criação de uma US (humano ou AI):

- Sempre que devolver instruções em lista, a introdução da lista deve começar com `:`;
- Os itens da lista devem terminar com `;`, exceto o último item da lista;
- O último item da lista deve terminar com `.`;
- Quando algum serviço, banco de dados, tabela ou algo parecido for citado, **pedir contexto** para saber como isso se encaixa na estória e se deve ou não ser alterado;
- É possível **sugerir** valores razoáveis (ex: stakeholder), mas sempre confirmar antes se de fato será usado;
- Se faltar detalhes nas informações fornecidas, **questionar**;
- Quando questionar algo, **enumerar** para facilitar a resposta.

### 3.5 Ciclo de vida e transições de estado/coluna

Use os estados, colunas e regras de transição do board do projeto. Algumas ferramentas tratam a coluna separadamente do estado do item.

Após confirmar a abertura do pull request ou merge request, vincule-o ao item. Aplique a transição de revisão quando as condições do time forem atendidas (por exemplo, quando o PR sair de rascunho) e o fluxo atribuir a ação ao agente. Se a etapa estiver indefinida, registre o vínculo e confirme o destino antes de mover. Resolução e encerramento seguem a convenção do projeto e são manuais por padrão.

---

## 4. Tasks dentro dos tickets de User Story

Aqui devem ser colocadas as atividades que serão realizadas para que a User Story chegue em produção ou entregue valor ao negócio.

### 4.1 Diretrizes

- A descrição da Task é **opcional** (quando o título for suficiente, não é necessário descrição);
- Quando houver descrição, deve ser concisa e objetiva, tentando se limitar a um ou dois parágrafos;
- Idealmente as Tasks são **antecipadas durante a criação do próprio User Story**, mas também é aceitável que novas Tasks sejam adicionadas conforme o progresso da implementação revele necessidades não previstas inicialmente.

### 4.2 Formato do título

Os títulos devem usar **verbos no infinitivo**.

Exemplos:

- Criar serviço xpto;
- Criar endpoint xyz;
- Prototipar/Implementar Tela xyz;
- Criar modelo DER;
- Realizar testes unitários;
- Criar/Abrir Pull Request;
- Gerar Evidências;
- Preparar GMUD;
- Publicar Estória.

### 4.3 Tasks padrão

| Task                           | Quando usar                            |
| ------------------------------ | -------------------------------------- |
| `Analisar problema`            | **Apenas em Bugs**, como primeira Task |
| `Gerar evidência da estória`   | Última Task de toda User Story         |
| `Gerar evidências de correção` | Última Task de todo Bug                |

> **Importante:** "Analisar problema" **não se aplica a User Stories** — US começam direto pela primeira ação concreta de implementação.

---

## 5. Padrão de Prototipação

Quando o desenvolvimento envolve um esforço de prototipação:

- A **implementação inicial** entra dentro de uma User Story de **prototipação**, mesmo se cobrir grande parte do escopo;
- O **polimento que transforma o protótipo em interface pronta para produção** é registrado em uma **nova User Story** que representa a entrega para produção;
- A US de prototipação é fechada quando o protótipo está pronto; a US de produção é criada na sequência para cobrir o polimento final.

Esse padrão evita misturar entregas de natureza diferente (exploração visual vs. entrega de produção) em uma única estória.

---

## 6. Componentes Compartilhados

Quando um componente shared (ex: tabela paginada genérica, header genérico) é introduzido durante o desenvolvimento de uma feature, faz mais sentido que ele **tenha como pai uma Feature de melhorias de UX/UI** (não a Feature da feature em curso), já que entrega valor ao projeto de modo geral. Confirmar com o time antes de mover.

---

## 7. Bugs

Para bugs, use o tipo nativo de defeito do board quando disponível. Caso contrário, use o tipo genérico com a classificação ou o rótulo de bug configurado pelo time. Convenções específicas:

- Primeira Task: `Analisar problema`;
- Última Task: `Gerar evidências de correção`;
- Tasks intermediárias: ações concretas (revisar código, corrigir, testar, preparar GMUD, deploy, etc.) no infinitivo.

---

## 8. Resumo do que NÃO fazer

- Classificar correção de defeito como entrega de funcionalidade → use a classificação de bug do board;
- Colocar contexto técnico extenso na descrição do Feature → manter macro;
- Usar User Story como diário da implementação → use o diário e registre comentários ou tarefas adicionais quando necessário;
- Iniciar título de US com verbo no infinitivo (`Buscar X`) ou com `Tela de X`;
- Ultrapassar 70 caracteres no título de US sem motivo claro;
- Usar `Analisar problema` como primeira Task de uma User Story;
- Encaixar componentes shared como filhos da Feature da feature em curso (devem ser filhos de uma Feature umbrella de melhorias).

---

## 9. Referências

- [Create Work Item](../processes/create-work-item.md) — procedimento para criar ou vincular itens;
- [Workflow](workflow.md) — fluxo de implementação com agentes, incluindo sincronização com o board.
