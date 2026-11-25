# Aprendizados — Desenvolvimento Assistido por IA "Agressivo"

> Lições generalizadas de uma implementação grande conduzida com IA (workflow brainstorm → spec → design → plano → subagent-driven development). São diretrizes destiladas e neutras de stack/empresa — os exemplos concretos foram trocados por princípios reutilizáveis. Os números entre colchetes mapeiam para os **Princípios** em [`../processes/start-workflow.md`](../processes/start-workflow.md).

---

## 1. Edições manuais em documentos gerados pela IA causam retrabalho [P1]

Quando você edita à mão um documento que a IA produziu (spec, design, plano), o orquestrador ainda tem a versão anterior no contexto e interpreta sua mudança intencional como erro de um subagente — e "reverte". Isso já causou renomear campos de volta, re-adicionar seções removidas de propósito e desfazer simplificações de URL.

**Recomendação:** peça ao orquestrador que faça a edição (assim ele atualiza sua representação interna e propaga para código, testes, plano, mock). Se a edição manual for inevitável, avise explicitamente o que mudou e por quê antes de prosseguir.

## 2. Higienize o codebase antes da implementação assistida [P2]

Código morto e artefatos não utilizados poluem discovery, design e implementação: a IA trata tudo que encontra como potencialmente relevante e propaga o ruído para documentos, planos e código. Um componente não usado entrou no escopo, foi implementado e depois removido — puro desperdício. Remova código morto **antes** de começar.

## 3. Subagente de review em paralelo e testes concorrentes brigam entre si [P3]

Despachar um reviewer em background enquanto o orquestrador edita os **mesmos** arquivos faz o reviewer reverter mudanças legítimas (trabalhou sobre a versão antiga). E muitos test runners (ex. Vitest) **não suportam instâncias concorrentes** no mesmo projeto — execuções simultâneas falham por timeout.

**Recomendação:** ou **sequencial** (termine, commite, depois revise), ou **paralelo com isolamento** — o prompt do reviewer lista os arquivos em edição e instrui a NÃO tocá-los e a NÃO rodar testes se outro agente puder estar rodando.

## 4. Code review por subagente dedicado é indispensável [P4]

O review feito pelo próprio orquestrador tende a ser superficial (leu poucos arquivos, declarou "ok"). Um subagente dedicado de review leu todos os arquivos, cruzou com spec/design e encontrou dezenas de issues reais.

**Recomendação:** review obrigatório por subagente dedicado **após cada fase**. O **mesmo** subagente deve corrigir o que não exige decisão do usuário (evita um round-trip). Só escale ao usuário o que depende de decisão (ambiguidade de spec, escolha de design/nome).

## 5. Após 2-3 tentativas falhas num ajuste visual, delegue [P5]

Um ajuste de CSS/foco passou por 6 tentativas manuais sem sucesso. Delegar a um subagente com **validação visual via Playwright MCP** (navegar, focar, screenshot, inspecionar computed styles) resolveu em uma iteração — ele achou a causa raiz real.

**Recomendação:** ao falhar 2-3 vezes num ajuste visual: pare de iterar, delegue a um subagente com Playwright MCP, exija validação por screenshot e **inclua o histórico de tentativas falhas** no prompt (para não repetir as mesmas abordagens).

## 6. Porte do fluxo conforme o tamanho da demanda [P6, P7]

Delegar produção de documentos/código a subagentes mantém o orquestrador ágil e permite paralelismo — mas custa **mais tokens** (cada subagente re-lê documentos de referência).

- **Trabalho grande (>50 arquivos):** subagentes compensam (contexto fresco, paralelismo).
- **Trabalho pequeno (<20 arquivos):** execução **inline** (Fluxo Express) economiza tokens e cerimônia.
- **Agrupe** tasks relacionadas num subagente grande em vez de muitos pequenos.
- **Cole o texto da task no prompt** do subagente em vez de mandá-lo abrir um plano gigante — ele lê o arquivo inteiro e desperdiça contexto.

## 7. Fases paralelas com dependências cruzadas precisam de integração explícita [P8]

Worktrees paralelas são cópias isoladas: TODOs de uma fase não se resolvem na outra. Resultado real: botões viraram no-ops porque os dialogs existiam mas não foram conectados.

**Recomendação:** sempre planeje um **passo de integração** quando duas fases paralelas têm dependências cruzadas — ou execute a dependente em sequência. No plano, marque o que é "integração" vs. "implementação pura".

## 8. Dados mock devem passar nas regras de negócio [P9]

Dados de mock gerados arbitrariamente (ex.: CPFs com dígito verificador inválido) são rejeitados pelos validadores do projeto, tornando o fluxo intestável. A causa raiz: o plano continha dados inválidos e o subagente os copiou fielmente, sem nenhum review cruzar mock × validators.

**Recomendação:** dados de mock/fixtures devem ser válidos segundo as regras implementadas (CPF, CNPJ, email, telefone…). Cruze isso no code review.

## 9. Lint e typecheck antes da suíte de testes [P10]

Rodar a suíte completa para descobrir um erro de tipo gasta 55-75s; `lint` + `typecheck` pegam o mesmo erro em 3-12s. **Ordem:** lint → typecheck → testes. Economiza ciclos longos de feedback e tokens quando um subagente itera.

## 10. Use o modelo mais capaz onde a decisão importa [P11]

O uso do modelo mais capaz na **orquestração, design e review** produziu implementações mais fiéis e menos retrabalho. Tasks mecânicas bem especificadas (entities, DTOs, mappers) podem usar modelos mais rápidos.

## 11. Diário de implementação incremental, não retroativo [P12]

Manter um `diario-implementacao.md` atualizado **a cada fase** documenta decisões que não cabem no código, registra métricas e captura lições no momento (antes do contexto se perder). Reconstruir tudo no fim é trabalhoso e impreciso. O orquestrador tende a pular a documentação — lembre proativamente.

## 12. Sincronize o tracker proativamente, não retroativamente [P13]

Popular o board (Azure DevOps / Jira / etc.) retroativamente a partir de commits e do diário é trabalhoso e gera estimativas imprecisas. O ideal é alimentar o tracker **durante** a implementação:

1. No discovery, pergunte o **ID do épico/feature** que será o parent dos work items.
2. Ao criar o plano, crie o **work item** de cada fase (filho do épico) e registre o ID no plano/diário.
3. Ao concluir cada fase (após review), atualize o work item: tasks, critérios aceitos, timetracking, estado.
4. Inclua o ID do tracker (ex.: `#1234`) junto à fase nos `.md` para rastreabilidade bidirecional documento ↔ tracker.

## 13. Testes E2E: Page Object Model + `data-testid`

E2E com seletores CSS diretos e lógica inline envelhece mal. Padrão recomendado: **Page Object Model** (classes que encapsulam seletores e ações por página) + **`data-testid`** como seletor principal (em vez de classes CSS). Ver [`e2e.md`](e2e.md).
