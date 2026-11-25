# Processo de Work Items

> Documento de referência canônico para criação e organização de work items no Azure DevOps Board do projeto.
> Este processo é aplicado por humanos e pelas skills de AI (ver `processes/create-work-item.md`).

---

## 1. Hierarquia

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

Um User Story é uma entrega que gera valor ao negócio. Obrigatoriamente deve pertencer a uma Feature. **Não deve ser usado para bugs** (use o tipo `Bug` próprio do Azure DevOps).

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

> **Critérios de Aceite vão no campo dedicado `Acceptance Criteria`** do Azure
> DevOps (referência interna `Microsoft.VSTS.Common.AcceptanceCriteria`),
> **NÃO** no Description. Esse campo é first-class na US/Bug e permite filtros,
> queries WIQL e relatórios baseados em ACs. Veja a seção 3.2.1 abaixo.

### 3.2.1 Campo Acceptance Criteria (separado da descrição)

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

### 3.3 Diretrizes de redação (Description + Acceptance Criteria)

- A parte `Eu, como [Stakeholder], necessito que [...], para que [...]` precisa ser o mais resumida e sucinta possível;
- Na parte `CONTEXTO`, deve ter o máximo de detalhes possíveis para que o time entenda o que precisa ser feito;
- User Stories **não devem servir como diário da implementação** — quando necessário documentar detalhes adicionais relevantes, isso pode ser feito na seção de `Discussion` (comentários) do ticket;
- Quando houver um esforço/ação que se encaixa melhor como Task, é melhor criar um Task ao invés de usar a seção de Discussion.

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

Ao longo da implementação, a User Story passa pelos estados (`System.State`)
e pelas colunas do board (`System.BoardColumn`). No board do projeto `<AZURE_PROJECT>`,
algumas colunas são sub-divisões do mesmo estado base — por exemplo
`Doing / Fixing / Testing` e `Waiting PR Approve` ambas mapeiam para
`System.State = Active`.

#### Transições automáticas (executadas pela AI via MCP)

- **Ao abrir o Pull Request** que entrega a estória, mover a US para a
  coluna `Waiting PR Approve` (state continua `Active`):

  ```
  wit_update_work_item({
    id: <US_ID>,
    updates: [
      { op: "replace", path: "/fields/System.BoardColumn", value: "Waiting PR Approve" }
    ]
  })
  ```

  A AI deve fazer isso logo após `gh pr create` retornar com sucesso.

#### Transições manuais (humano executa)

- `Resolved` → `Closed`: permanecem manuais conforme convenção do time. A AI
  **não** marca como Resolved automaticamente, apenas pode lembrar o usuário
  ao final do fluxo se relevante.

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

Bugs **não são User Stories**. Devem usar o tipo nativo `Bug` do Azure DevOps. Convenções específicas:

- Primeira Task: `Analisar problema`;
- Última Task: `Gerar evidências de correção`;
- Tasks intermediárias: ações concretas (revisar código, corrigir, testar, preparar GMUD, deploy, etc.) no infinitivo.

---

## 8. Resumo do que NÃO fazer

- Criar User Story para corrigir bug → use o tipo `Bug`;
- Colocar contexto técnico extenso na descrição do Feature → manter macro;
- Usar User Story como diário da implementação → use Discussion ou Tasks adicionais;
- Iniciar título de US com verbo no infinitivo (`Buscar X`) ou com `Tela de X`;
- Ultrapassar 70 caracteres no título de US sem motivo claro;
- Usar `Analisar problema` como primeira Task de uma User Story;
- Encaixar componentes shared como filhos da Feature da feature em curso (devem ser filhos de uma Feature umbrella de melhorias).

---

## 9. Referências

- Skill `processes/create-work-item.md` — automação do processo via Claude Code;
- Documento `docs/workflow.md` — workflow completo de implementação com AI (incluindo sincronização com o Board).
