# Integrações por capacidade

Escolha os serviços que o projeto já usa para cada capacidade. O host Git, o board e o destino da documentação podem ser independentes. O [procedimento de integração](../processes/integrar.md) usa este contrato para propor a configuração e registrá-la na [referência do projeto](../templates/project-reference.template.md).

## Contrato de integração

Registre uma linha por operação relevante na referência do projeto. Operações com permissões, conectores ou alternativas diferentes ficam em linhas separadas.

| Campo | O que registrar |
| --- | --- |
| Capacidade e operação | Ex.: board / mover item, Git / publicar review, CI / consultar execução. |
| Provedor e destino | Serviço, edição SaaS ou self-hosted quando aplicável, URL e escopo (organização, workspace, projeto, repositório ou board). |
| Cliente e caminho principal | Ferramenta de IA que executa a operação e conector MCP, CLI ou API disponível nela. |
| Acesso | Tipo de autenticação, permissões necessárias e quem pode executar a operação. Descreva a origem da credencial sem registrar seu valor. |
| Alternativa | Caminho confirmado por CLI, API, interface manual ou registro local. Se nenhum estiver disponível, indique o que fica pendente. |
| Estado e evidência | Use os estados da matriz abaixo e registre ambiente, operação e resultado para as verificações do projeto. |

Na descoberta, confirme o destino e as operações disponíveis com consultas de leitura quando houver acesso autorizado. Para operações de escrita, siga o fluxo e as permissões do projeto. Se uma escrita retornar resultado incerto, confira o estado no serviço antes de tentar uma alternativa. Na ausência de integração, mantenha o trabalho local e descreva a ação manual, quando aplicável.

## Matriz inicial

**Verificado** significa que a operação indicada foi exercitada no ambiente citado. **Documentado no kit** significa que existe um procedimento ou script no kit, com o nível de teste indicado. **Candidato** significa que a configuração ou API do fornecedor pode servir de base para uma integração futura. A presença de uma operação na documentação do fornecedor não confirma que ela está exposta no cliente, no plano ou na instância do projeto.

| Capacidade | Provedor e ambiente | Operações e caminho | Acesso e alternativa | Estado |
| --- | --- | --- | --- | --- |
| Board | Azure DevOps | Consulta, criação, atualização e vínculos pelo MCP. | Acesso ao projeto e permissão para a operação; Azure CLI quando configurada. [Setup](../processes/setup-azure-mcp.md) | Documentado no kit. |
| Board | Jira Cloud | Consulta, criação e transições pelo Atlassian Rovo MCP. | Acesso ao site e permissões da operação; REST ou interface manual. Jira Data Center requer configuração separada. [Setup](../processes/setup-jira.md) · [Ferramentas Rovo](https://developer.atlassian.com/cloud/rovo-mcp/guides/supported-tools/) | Documentado no kit. |
| Board | GitHub Projects, GitHub.com | Consultar o projeto, adicionar cartões e editar campos/status por GitHub CLI ou GraphQL. O item do board e a issue têm IDs próprios. | Permissão no Project e, para operações sobre a issue, no repositório; interface web como alternativa manual. [API de Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects) | Verificado para listagem, adição de cartões e edição de campos no [Project #6](https://github.com/users/Ghostavio/projects/6), usando Codex e `gh`/GraphQL. |
| Board | Linear, SaaS | Consultar issues/projetos e criar ou atualizar issues pelo MCP oficial. | OAuth com acesso ao time e à operação; API GraphQL ou interface manual. [Linear MCP](https://linear.app/docs/mcp) | Candidato. |
| Board | Trello, ClickUp e OpenProject | Cartões, tarefas ou work packages; avaliar consulta, vínculo e transições separadamente. | Confirmar API, edição e permissões por serviço, incluindo OpenProject self-hosted. | Candidatos. |
| Git / revisão | GitHub.com | Ler diff, abrir PR, comentar e mesclar pelo conector GitHub. | Acesso ao repositório e permissões de PR; `gh` ou interface manual. Aprovação e merge seguem as regras do repositório. | Verificado para leitura, abertura, comentário e merge no [Symbiote-AI](https://github.com/Ghostavio/Symbiote-AI/pull/24), usando Codex e o conector GitHub. |
| Git / revisão e CI | Bitbucket Cloud | Consulta de repositório/diff, operações de PR e consulta de pipelines pelo Atlassian Rovo MCP. | Workspace vinculado à organização Atlassian, acesso à aplicação e permissões de leitura/escrita; API ou interface manual. [Ferramentas Rovo](https://developer.atlassian.com/cloud/rovo-mcp/guides/supported-tools/#bitbucket-cloud) | Candidato. O suporte Cloud não implica suporte Data Center. |
| Git / revisão e CI | GitLab.com e GitLab Self-Managed | Avaliar acesso a projetos, MRs e pipelines. Verificar quais operações o MCP oficial expõe na instância e mapear as restantes. | Confirmar edição, versão, configuração e permissões; `glab`, API ou interface manual. [GitLab MCP](https://docs.gitlab.com/user/model_context_protocol/mcp_server/) | Candidato. Validar os dois ambientes separadamente. |
| CI | GitHub Actions | Consultar checks e logs; o kit inclui uma pipeline de validação. | Acesso aos checks e logs do repositório; CLI, API ou interface manual. | Pipeline documentada no kit; consulta de checks via `gh pr view` exercitada no repositório do kit. |
| Documentação | Git e Confluence | Docs no repositório ou publicação externa conforme o destino do projeto. | Permissão no repositório ou espaço; arquivo local e link manual quando necessário. [Escolher destino](../processes/docs-target.md) | Documentado no kit. |
| Registro de horas | 7pace e Clockify | Simular e registrar por provedor; o wrapper também permite selecionar um provedor para retomar um envio parcial. | Credenciais do provedor apenas para envio real; diário local como alternativa. [Timesync](../processes/timesync.md) | Scripts no kit; dry run e falhas HTTP exercitados com respostas simuladas. |
| Comunicação | Slack, Teams ou outro canal do time | Avaliar leitura de contexto e publicação de atualizações como operações separadas. | Confirmar workspace, canal e permissão de publicação; resumo local para envio manual. | Candidatos. |
| Qualidade e observabilidade | Análise estática local, SonarQube e OpenTelemetry | Rodar verificações locais, consultar análise centralizada quando configurada e seguir as convenções de instrumentação do projeto. | Linter local como primeira opção; acesso de leitura para serviços externos. [Revisão](../processes/phase-code-review.md) | Documentado no kit. |

Para detalhes de descoberta e nomes de ferramentas por cliente de IA, consulte a [matriz de ferramentas](../ai-tools-matrix.md).

## Exemplos de composição

- **Linear + GitLab + docs no Git:** use o Linear para o item de trabalho, o GitLab para o MR e os checks e o repositório para a especificação. O vínculo entre item e MR pode ser uma URL quando a integração nativa não estiver disponível.
- **Jira + Bitbucket Cloud + Confluence:** use as três capacidades separadamente, ainda que o Atlassian Rovo MCP seja o conector comum. A permissão de editar uma issue não define as permissões para publicar uma página ou mesclar um PR.

Para promover uma operação a **Verificado**, registre em um ambiente autorizado o cliente, o conector, a edição/versão quando relevante, a data, a ação executada e o resultado. Teste leitura e escrita separadamente. Uma verificação em um serviço ou conta não certifica outros ambientes.
