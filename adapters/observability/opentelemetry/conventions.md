# Adaptador de Observabilidade — OpenTelemetry

Convenções recomendadas para projetos com instrumentação de observabilidade baseada em **OpenTelemetry** (compatível via OTLP com Grafana/Tempo/Loki/Prometheus, Datadog, Honeycomb, New Relic, AWS CloudWatch/X-Ray, entre outros) acoplados ao **Symbiote-AI**. Ao aplicar este adaptador via `simbiose`, ajuste a linguagem/SDK e o backend OTLP reais no `.claude/PROJECT_REFERENCE.md`.

## Instrumentação neutra de fornecedor

- **API padrão e exportação via OTLP:** instrumente código da aplicação com a API OpenTelemetry (`@opentelemetry/api`, `opentelemetry-api`, `go.opentelemetry.io/otel`, etc.) e concentre a configuração do SDK/exportador no bootstrap do serviço — evitando acoplar regras de domínio a SDKs proprietários.
- **Atributos de recurso consistentes:** defina `service.name`, `service.version` e `deployment.environment.name` via configuração de ambiente, sem endpoints ou credenciais hardcoded no código.

## Os três pilares correlacionados

### Logs estruturados
- Emita logs estruturados (JSON) com níveis coerentes (`error`, `warn`, `info`, `debug`) em vez de `console.log`/`print` soltos em código de produção.
- Correlacione automaticamente logs ao contexto de trace ativo (`trace_id`, `span_id`), facilitando saltar de um alerta ou log para o trace distribuído completo.
- Registre o erro na fronteira apropriada com contexto suficiente para diagnóstico, evitando duplicar o mesmo stack trace em todas as camadas da pilha.

### Tracing distribuído
- **Propagação de contexto:** preserve W3C Trace Context (`traceparent` / `tracestate`) em chamadas HTTP, gRPC, workers e mensagens de fila.
- **Nomes de spans com baixa cardinalidade:** use rotas parametrizadas e nomes estáveis (`GET /orders/:id`, `orders.create`), nunca URLs cruas contendo IDs dinâmicos ou query strings.
- **Ciclo de vida seguro:** garanta o encerramento explícito de todos os spans criados manualmente — em JS/TS, mesmo dentro de `startActiveSpan`, o callback ainda precisa chamar `span.end()` em um bloco `try/finally` (ou usar um wrapper que garanta o fechamento); em Python use `with tracer.start_as_current_span(...)` e em Go use `defer span.End()`. Em falhas, chame `recordException(err)` e marque status `ERROR`.

### Métricas (RED / USE) e controle de cardinalidade
- Priorize sinais **RED** (Rate, Errors, Duration) para serviços/APIs e **USE** (Utilization, Saturation, Errors) para recursos/filas.
- **Regra crítica de cardinalidade:** nunca coloque valores de alta cardinalidade em atributos/labels de métricas (`user_id`, `tenant_id` ilimitado, `request_id`, UUIDs, e-mails, timestamps ou URLs completas) — isso causa explosão de séries temporais, memória e custo.

## Privacidade, segurança e redação (PII / Segredos)

- **Zero segredos ou PII bruta na telemetria:** nunca grave cabeçalhos `Authorization`, `Cookie`, API keys, senhas, CPF, dados de pagamento ou payloads inteiros de requisição/resposta em logs, atributos de span ou eventos.
- Aplique listas de permissão (allowlist) ou redação centralizada de campos sensíveis nos middlewares de logging e no Collector OTel.

## Ciclo de vida, custo e SLOs

- **Flush/shutdown gracioso:** em servidores, chame `sdk.shutdown()` no encerramento gracioso (`SIGTERM`/`SIGINT`); em jobs efêmeros, CLIs, Lambdas ou Workers, garanta `forceFlush()` (ex.: antes do fim da execução ou via `ctx.waitUntil(...)`) para não perder os últimos spans/métricas.
- **Volume e sampling:** evite logs `info`/`debug` dentro de loops quentes ou retries acelerados; configure sampling coerente com o volume de produção (head ou tail sampling no Collector).
- **SLOs e alertas acionáveis:** derive alertas de sintomas que afetam o usuário (taxa de erro, latência p95/p99, burn rate de SLO) associados a contexto/runbook, em vez de alertar sobre ruído transitório.
