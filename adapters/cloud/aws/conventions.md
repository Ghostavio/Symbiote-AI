# Adaptador de Cloud — AWS

Convenções recomendadas para projetos com workloads ou Infraestrutura como Código (IaC) na **AWS** acoplados ao **Symbiote-AI**. Ao aplicar este adaptador via `simbiose`, incorpore apenas os serviços e a ferramenta de IaC realmente usados no projeto host (CDK, Terraform, SAM, SST, CloudFormation) e registre os comandos confirmados no `.claude/PROJECT_REFERENCE.md`.

## IAM, identidades e segredos

- **Menor privilégio estrito:** conceda apenas as ações e os ARNs necessários para cada recurso; evite `Action: "*"` ou `Resource: "*"` salvo exceções documentadas por limitação do serviço AWS.
- **Credenciais temporárias:** prefira IAM Roles e OIDC (ex.: GitHub Actions/GitLab OIDC, instance/task/execution roles) — nunca versione access keys estáticas (`AKIA...`), tokens ou perfis privados no repositório.
- **Gestão de segredos:** armazene segredos no AWS Secrets Manager ou SSM Parameter Store (`SecureString`), nunca em texto plano em variáveis de ambiente de templates IaC, logs ou artefatos de build.

## Infraestrutura como Código (IaC) e governança

- **Tudo versionado em IaC:** declare recursos, políticas, filas, buckets e alarmes via a stack de IaC do projeto (evite mudanças manuais ad-hoc no console sem refletir no código).
- **Isolamento e tagging:** separe ambientes por conta/região ou prefixo consistente e aplique tags padronizadas (`service`, `env`, `owner`) para rastreabilidade e governança de custos.
- **Retenção explícita de logs:** configure período de retenção em CloudWatch Log Groups (evite retenção infinita por padrão) e lifecycle rules em buckets S3 quando aplicável.

## Compute e Serverless (Lambda, ECS/EKS, API Gateway)

- **Inicialização fora do handler:** em AWS Lambda, instancie clientes de SDK (preferindo AWS SDK v3 modular em JS/TS) e pools reutilizáveis no escopo do módulo para aproveitar warm starts, sem guardar estado mutável específico de usuário/requisição em variáveis globais.
- **Timeouts e concorrência:** defina timeouts explícitos e coerentes com o chamador (ex.: Lambda atrás de API Gateway abaixo do limite do gateway) e configure limites de concorrência/memória proporcionais à carga.
- **Desacoplamento:** mantenha regras de domínio independentes dos adapters de evento AWS (API Gateway, SQS, EventBridge, S3), facilitando testes unitários locais sem depender da nuvem.

## Dados, mensageria e resiliência

- **SQS / SNS / EventBridge / Step Functions:**
  - Trate entregas como *at-least-once* com consumidores **idempotentes**.
  - Configure **Dead-Letter Queue (DLQ)** com alarme e `visibilityTimeout` adequadamente superior ao timeout do consumidor (regra prática: ≥ 6× o timeout da Lambda).
  - Em lotes SQS → Lambda, habilite `reportBatchItemFailures` quando falhas parciais puderem ocorrer, evitando reprocessar o lote inteiro.
- **S3:** mantenha `BlockPublicAccess` habilitado em buckets privados, criptografia em repouso/trânsito (HTTPS-only) e validação de chaves/prefixos.
- **DynamoDB e bancos relacionais (RDS/Aurora):** evite `Scan` sem paginação em DynamoDB (prefira `Query` com índices e limites explícitos); sempre trate tokens de paginação (`NextToken`/`LastEvaluatedKey`); em workloads serverless acessando RDS, use pooling adequado (ex.: RDS Proxy) para evitar exaustão de conexões.
- **Prevenção de loops recursivos:** nunca permita que uma função acionada por evento (S3, SQS, DynamoDB Streams) grave no mesmo recurso/prefixo que dispara a própria função sem condição de parada explícita.

## Verificações locais e segurança operacional

- **Comandos confirmados:** registre no `.claude/PROJECT_REFERENCE.md` apenas ferramentas e scripts instalados no host (`cdk`, `terraform`, `sam`, `cfn-lint`, testes unitários de IaC).
- **Sem mutações em revisão:** durante revisões ou verificações automatizadas, execute apenas validações locais/offline (`synth`, `validate`, `fmt -check`, `lint`, testes unitários). Nunca execute `deploy`, `apply` ou comandos destrutivos na conta AWS sem aprovação explícita.
