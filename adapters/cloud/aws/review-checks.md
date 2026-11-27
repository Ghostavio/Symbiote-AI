# Review Checks — Adaptador AWS

Checklist especializado para carregar em [`processes/phase-code-review.md`](../../../processes/phase-code-review.md) (§2, §3, §4 e §7–§8) quando o adaptador `aws` estiver acoplado ao projeto.

## §2 Code Quality & Patterns (AWS)

- [ ] Em JS/TS, uso de clientes modulares do AWS SDK v3 (`@aws-sdk/client-*`) em vez de importar bundles monolíticos.
- [ ] Clientes AWS SDK inicializados fora do handler da Lambda para reaproveitar conexões em warm starts, sem armazenar estado mutável de usuário/requisição em escopo global.
- [ ] Operações paginadas da API AWS tratam `NextToken` / `LastEvaluatedKey` / paginators sem truncar resultados silenciosamente.
- [ ] Regras de domínio separadas dos adaptadores de entrada/saída AWS (handlers de API Gateway, SQS, EventBridge, S3, DynamoDB).

## §3 Architecture & Layer Consistency (AWS)

- [ ] Novos recursos, permissões IAM e variáveis declarados na ferramenta de IaC adotada pelo projeto (CDK, Terraform, SAM, SST, CloudFormation) com tagging e isolamento por ambiente.
- [ ] Filas/tópicos assíncronos configurados com DLQ, política de retry coerente e suporte a `reportBatchItemFailures` em processamento em lote SQS quando aplicável.
- [ ] Consumidores assíncronos garantem idempotência para entrega *at-least-once*.
- [ ] Retenção explícita configurada para CloudWatch Log Groups criados ou alterados.

## §4 Bug Detection, Security & Cost (AWS)

- [ ] **IAM & Segredos:** ausência de `Action: "*"` / `Resource: "*"` sem justificativa, zero access keys hardcoded (`AKIA...`), zero segredos em texto plano em variáveis de ambiente ou templates IaC.
- [ ] **Exposição de dados:** buckets S3 privados mantêm `BlockPublicAccess` habilitado e exigem TLS; políticas de recurso não abrem acesso amplo (`Principal: "*"`) indevidamente.
- [ ] **Loops recursivos e custo:** nenhum trigger (S3, SQS, DynamoDB Streams) reescreve no mesmo recurso/prefixo gerando invocação infinita; ausência de `Scan` irrestrito em tabelas DynamoDB de produção.
- [ ] **Timeouts e conexões:** `visibilityTimeout` de SQS compatível com o timeout do consumidor (≥ 6× em Lambda); timeout de Lambda compatível com o upstream; acesso a RDS a partir de serverless considera limites de conexão/pooling.

## §7–§8 Quality Checks (exemplos condicionais AWS)

Execute **apenas** ferramentas e scripts realmente instalados e confirmados no projeto host (`.claude/PROJECT_REFERENCE.md`), restringindo revisões a validações locais/offline. **Nunca** execute `deploy`, `apply` ou mutações em contas AWS sem autorização explícita do usuário.

Exemplos condicionais (somente quando a respectiva ferramenta estiver instalada e configurada no host; pule etapas que dependam de lookups remotos ausentes no cache local ou de bundling indisponível):

```bash
npm test                                      # testes unitários de handlers e assertions/snapshots de IaC
terraform fmt -check && terraform validate    # somente em projetos Terraform já inicializados localmente
./node_modules/.bin/cdk synth --no-lookups    # somente em projetos CDK cujo app de síntese/bundling rode localmente; desativa lookups na AWS (pule se faltar contexto local)
sam validate                                  # somente em projetos AWS SAM com CLI instalada
```
